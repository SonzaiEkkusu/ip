import requests
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_proxy(row, api_url_template):
    ip, port = row[0].strip(), row[1].strip()
    api_url = api_url_template.format(ip=ip, port=port)
    try:
        response = requests.get(api_url, timeout=60)
        response.raise_for_status()
        data = response.json()

        proxy_status = data.get("proxyStatus", "").strip()
        status = proxy_status == "✅ ALIVE ✅"

        if status:
            print(f"{ip}:{port} is ALIVE")
            return (row, None)
        else:
            print(f"{ip}:{port} is DEAD")
            return (None, f"{ip}:{port} is DEAD")

    except requests.exceptions.RequestException as e:
        error_message = f"Error checking {ip}:{port}: {e}"
        print(error_message)
        return (None, error_message)
    except ValueError as ve:
        error_message = f"Error parsing JSON for {ip}:{port}: {ve}"
        print(error_message)
        return (None, error_message)

def main():
    input_file = os.getenv('IP_FILE', 'proxy.txt')
    output_file = 'proxy_updated.txt'
    error_file = 'errorproxy.txt'
    api_url_template = os.getenv('API_URL', 'https://apix.sonzaix.us.kg/?ip={ip}:{port}')

    alive_proxies = []
    error_logs = []

    try:
        with open(input_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"File {input_file} tidak ditemukan.")
        return

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_proxy, row, api_url_template): row for row in rows if len(row) >= 2}

        for future in as_completed(futures):
            result, error = future.result()
            if result:
                alive_proxies.append(result)
            if error:
                error_logs.append(error)

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(alive_proxies)

    with open(error_file, "w") as f:
        for error in error_logs:
            f.write(error + "\n")

    print("Proses selesai. Cek proxy_updated.txt dan errorproxy.txt.")

if __name__ == "__main__":
    main()