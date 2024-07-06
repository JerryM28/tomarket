import os
import sys
import json
import time
import random
import argparse
import requests
from datetime import datetime
from urllib.parse import parse_qs
from colorama import init, Fore, Style
import base64

# Inisialisasi colorama
init()

# Warna untuk tampilan konsol
merah = Fore.LIGHTRED_EX
kuning = Fore.LIGHTYELLOW_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX
putih = Fore.LIGHTWHITE_EX
hitam = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
line = putih + "♡" * 55


class Tomartod:
    def __init__(self):
        self.headers = {
            "host": "api-web.tomarket.ai",
            "connection": "keep-alive",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "content-type": "application/json",
            "origin": "https://mini-app.tomarket.ai",
            "x-requested-with": "tw.nekomimi.nekogram",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mini-app.tomarket.ai/",
            "accept-language": "en-US,en;q=0.9",
        }
        self.marinkitagawa = lambda data: {
            key: value[0] for key, value in parse_qs(data).items()
        }

    def set_authorization(self, auth):
        self.headers["authorization"] = auth

    def del_authorization(self):
        if "authorization" in self.headers.keys():
            self.headers.pop("authorization")

    def login(self, data):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/login"
        data = json.dumps(
            {
                "init_data": data,
                "invite_code": "",
            }
        )
        self.del_authorization()
        res = self.http(url, self.headers, data)
        if res.status_code != 200:
            self.log(f"{merah}Gagal mendapatkan kamar hotel, cek http.log !")
            return None
        token = res.json()["data"]["access_token"]
        return token

    def start_farming(self):
        data = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/start"
        res = self.http(url, self.headers, data)
        if res.status_code != 200:
            self.log(f"{merah}Gagal bercocok tanam, cek http.log baris terakhir !")
            return False

        data = res.json().get("data")
        end_farming = data["end_at"]
        format_end_farming = datetime.fromtimestamp(end_farming).strftime("%H:%M:%S")
        self.log(f"{hijau}Berhasil bercocok tanam!")

    def end_farming(self):
        data = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/claim"
        res = self.http(url, self.headers, data)
        if res.status_code != 200:
            self.log(f"{merah}Ngecrot diluar, cek http.log baris terakhir !")
            return False

        poin = res.json()["data"]["claim_this_time"]
        self.log(f"{hijau}Ngecrot didalem!")
        self.log(f"{hijau}Hadiah: {putih}{poin}")

    def daily_claim(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/daily/claim"
        data = json.dumps({"game_id": "fa873d13-d831-4d6f-8aee-9cff7a1d0db1"})
        res = self.http(url, self.headers, data)
        if res.status_code != 200:
            self.log(f"{merah}pakai pengaman, cek http.log baris terakhir !")
            return False

        try:
            data = res.json().get("data")
            poin = data["today_points"]
            self.log(
                f"{hijau}membeli {biru}pengaman{hijau}, harga: {putih}{poin} !"
            )
        except Exception as e:
            self.log(f"{merah}gagal membeli pengaman: {str(e)}")
            return False
        
        return True

    def play_game_func(self, amount_pass):
        data_game = json.dumps({"game_id": "59bcd12e-04e2-404c-a172-311a0084587d"})

        start_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/play"
        claim_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/claim"
        for i in range(amount_pass):
            res = self.http(start_url, self.headers, data_game)
            if res.status_code != 200:
                self.log(f"{merah}Gagal masuk kamar!")
                return

            self.log(f"{hijau}Berhasil {biru}masuk{hijau} kamar!")
            self.countdown(30)
            point = random.randint(self.game_low_point, self.game_high_point)
            data_claim = json.dumps(
                {"game_id": "59bcd12e-04e2-404c-a172-311a0084587d", "points": point}
            )
            res = self.http(claim_url, self.headers, data_claim)
            if res.status_code != 200:
                self.log(f"{merah}Gagal crot dihotel!")
                continue

            self.log(f"{hijau}Berhasil {biru}crot{hijau} di hotel: {putih}{point}")

    def get_balance(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/balance"
        while True:
            res = self.http(url, self.headers, "")
            if res is None:
                self.log(f"{merah}Gagal mendapatkan cewe!")
                return None

            try:
                data = res.json().get("data")
                if data is None:
                    self.log(f"{merah}Tidak ada cewe!")
                    return None

                timestamp = data["timestamp"]
                balance = data["available_balance"]
                self.log(f"{hijau}Saldo: {putih}{balance}")

                if "daily" not in data.keys() or data["daily"] is None:
                    if not self.daily_claim():
                        continue

                next_daily = data["daily"]["next_check_ts"]
                if timestamp > next_daily:
                    if not self.daily_claim():
                        continue

                if "farming" not in data.keys():
                    self.log(f"{kuning}Bercocok tanam belum dimulai!")
                    result = self.start_farming()
                    continue

                end_farming = data["farming"]["end_at"]
                format_end_farming = datetime.fromtimestamp(end_farming).strftime("%H:%M:%S")
                if timestamp > end_farming:
                    self.end_farming()
                    continue

                self.log(f"{kuning}Belum waktunya bercocok tanam!")
                self.log(f"{kuning}Akhir bercocok tanam: {putih}{format_end_farming}")
                if self.play_game:
                    self.log(f"{hijau}Auto main dihotel aktif!")
                    play_pass = data.get("play_passes")
                    self.log(f"{hijau}Kunci Hotel: {putih}{play_pass}")
                    if int(play_pass) > 0:
                        self.play_game_func(play_pass)
                        continue

                _next = end_farming - timestamp
                return _next

            except Exception as e:
                self.log(f"{merah}Error saat memproses data: {str(e)}")
                return None

    def load_data(self, file):
        try:
            with open(file, 'r') as f:
                datas = f.read().splitlines()
            if len(datas) <= 0:
                self.log(f"{merah}File {file} tidak ada atau kosong!")
                sys.exit()
            return datas
        except Exception as e:
            self.log(f"{merah}Error saat memuat data dari {file}: {str(e)}")
            sys.exit()

    def load_config(self, file):
        try:
            with open(file, 'r') as f:
                config = json.load(f)
                self.interval = config["interval"]
                self.game_low_point = config["game_low_point"]
                self.game_high_point = config["game_high_point"]
                self.play_game = config["play_game"]
        except FileNotFoundError:
            self.log(f"{merah}File {file} tidak ditemukan!")
            sys.exit()
        except Exception as e:
            self.log(f"{merah}Error saat memuat konfigurasi dari {file}: {str(e)}")
            sys.exit()

    def save(self, id, token):
        try:
            with open("tokens.json", 'r') as f:
                tokens = json.load(f)
        except FileNotFoundError:
            tokens = {}

        tokens[str(id)] = token
        try:
            with open("tokens.json", 'w') as f:
                json.dump(tokens, f, indent=4)
        except Exception as e:
            self.log(f"{merah}Error saat menyimpan tokens.json: {str(e)}")

    def get(self, id):
        try:
            with open("tokens.json", 'r') as f:
                tokens = json.load(f)
                if str(id) not in tokens.keys():
                    return None
                return tokens[str(id)]
        except FileNotFoundError:
            return None
        except Exception as e:
            self.log(f"{merah}Error saat memuat tokens.json: {str(e)}")
            return None

    def is_expired(self, token):
        try:
            # Decode the token parts
            parts = token.split('.')
            if len(parts) != 3:
                self.log(f"{merah}Format token tidak valid: {token}")
                return True
            
            header, payload, sign = parts
            
            # Reconstruct payload and decode it
            payload += '=' * (-len(payload) % 4)
            decoded_payload = base64.urlsafe_b64decode(payload).decode('utf-8')
            payload_dict = json.loads(decoded_payload)
            
            # Check expiration time
            now = int(datetime.now().timestamp())
            if now > payload_dict["exp"]:
                return True
            return False
        except Exception as e:
            self.log(f"{merah}Error saat memeriksa kedaluwarsa token: {str(e)}")
            return True

    def http(self, url, headers, data=None):
        while True:
            try:
                now = datetime.now().isoformat(" ").split(".")[0]
                if data is None:
                    res = requests.get(url, headers=headers)
                    open("http.log", "a", encoding="utf-8").write(
                        f"{now} - {res.status_code} - {res.text}\n"
                    )
                    return res

                if data == "":
                    res = requests.post(url, headers=headers)
                    open("http.log", "a", encoding="utf-8").write(
                        f"{now} - {res.status_code} - {res.text}\n"
                    )
                    return res

                res = requests.post(url, headers=headers, data=data)
                open("http.log", "a", encoding="utf-8").write(
                    f"{now} - {res.status_code} - {res.text}\n"
                )
                return res
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                self.log(f"{merah}Kesalahan koneksi / waktu koneksi habis!")
                time.sleep(1)
                continue

    def countdown(self, t):
        for i in range(t, 0, -1):
            menit, detik = divmod(i, 60)
            jam, menit = divmod(menit, 60)
            jam = str(jam).zfill(2)
            menit = str(menit).zfill(2)
            detik = str(detik).zfill(2)
            print(f"{putih}LEMES {jam}:{menit}:{detik}     ", flush=True, end="\r")
            time.sleep(1)
        print("                                        ", flush=True, end="\r")

    def log(self, msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{hitam}[{now}]{reset} {msg}{reset}")

    def main(self):
        banner = f"""
    {hijau}Auto Claim {merah}Tomarket
    
    {hijau}By: {biru}JerryM
    {hijau}GRUP: {biru}WIMIX
        
        """
        arg = argparse.ArgumentParser()
        arg.add_argument("--data", default="data.txt")
        arg.add_argument("--config", default="config.json")
        arg.add_argument("--marinkitagawa", action="store_true")
        args = arg.parse_args()
        if not args.marinkitagawa:
            os.system("cls" if os.name == "nt" else "clear")
        print(banner)
        self.load_config(args.config)
        datas = self.load_data(args.data)
        self.log(f"{biru}Peserta: {putih}{len(datas)}")
        print(line)
        while True:
            list_countdown = []
            _start = int(time.time())
            for no, data in enumerate(datas):
                parser = self.marinkitagawa(data)
                user = json.loads(parser["user"])
                id = user["id"]
                self.log(
                    f"{hijau}Nomor Peserta: {putih}{no+1}{hijau}/{putih}{len(datas)}"
                )
                self.log(f"{hijau}Nama: {putih}{user['first_name']}")
                token = self.get(id)
                if token is None:
                    token = self.login(data)
                    if token is None:
                        continue
                    self.save(id, token)

                if self.is_expired(token):
                    token = self.login(data)
                    if token is None:
                        continue
                    self.save(id, token)
                self.set_authorization(token)
                result = self.get_balance()
                print(line)
                self.countdown(self.interval)
                list_countdown.append(result)
            _end = int(time.time())
            _tot = _end - _start
            _min = min(list_countdown) - _tot
            self.countdown(_min)


if __name__ == "__main__":
    try:
        app = Tomartod()
        app.main()
        print("Program selesai!")
        print(Style.RESET_ALL)  # Reset tampilan konsol ke default setelah program selesai
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
