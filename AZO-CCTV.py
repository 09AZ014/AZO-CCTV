import requests
import re
import colorama
from requests.structures import CaseInsensitiveDict

colorama.init()

# URLs das fontes de câmeras
sources = {
    "insecam": "http://www.insecam.org/en/jsoncountries/",
    # Outras fontes podem ser adicionadas aqui
}


def fetch_camera_sources():
    countries = {}
    for name, url in sources.items():
        try:
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["User-Agent"] = "Mozilla/5.0"

            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                if name == "insecam":
                    data = resp.json()
                    countries = data['countries']
                    print(f"[INFO] Dados da fonte {name} recebidos com sucesso.")
                else:
                    print(f"[INFO] Fonte {name} não implementada.")
            else:
                print(f"[ERROR] Não foi possível acessar {name}: Status {resp.status_code}")
        except requests.exceptions.SSLError:
            print(f"[ERROR] Erro SSL ao acessar {name}: {url}. Verifique a conexão.")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Erro ao acessar {name}: {url} - {e}")
        except Exception as e:
            print(f"[ERROR] Falha inesperada ao buscar dados de {name}: {e}")
    return countries


def get_camera_ips(country_code):
    try:
        url = f"http://www.insecam.org/en/bycountry/{country_code}"
        headers = CaseInsensitiveDict()
        headers["User-Agent"] = "Mozilla/5.0"
        res = requests.get(url, headers=headers)
        last_page = re.findall(r'pagenavigator\("\?page=", (\d+)', res.text)

        if last_page:
            last_page = int(last_page[0])
            all_ips = []

            for page in range(last_page):
                print(f"[INFO] Acessando página {page + 1} de {last_page} para o país {country_code}.")
                res = requests.get(f"{url}/?page={page}", headers=headers)
                find_ip = re.findall(r"http://\d+\.\d+\.\d+\.\d+:\d+", res.text)
                all_ips.extend(find_ip)

            if all_ips:
                with open(f'{country_code}.txt', 'w') as f:
                    for ip in all_ips:
                        print(f"\033[1;31m{ip}")
                        f.write(f'{ip}\n')
                print(f"\033[1;37m[INFO] Arquivo salvo: {country_code}.txt")
            else:
                print(f"[WARNING] Nenhum IP encontrado para o país {country_code}.")
        else:
            print(f"[ERROR] Não foi possível determinar o número de páginas para o país {country_code}.")
    except Exception as e:
        print(f"[ERROR] Ocorreu um erro ao buscar câmeras para o país {country_code}: {e}")


def main():
    print("""\033[1;31m\033[1;37m
  ______   ________   ______  
 /      \ |        \ /      \ 
|  $$$$$$\ \$$$$$$$$|  $$$$$$\\
| $$__| $$    /  $$ | $$  | $$ 
| $$    $$   /  $$  | $$  | $$ 
| $$$$$$$$  /  $$   | $$  | $$ 
| $$  | $$ /  $$___ | $$__/ $$ 
| $$  | $$|  $$    \ \$$    $$ 
 \$$   \$$ \$$$$$$$$  \$$$$$$  

\033[1;31m 09AZO14 \033[1;31m\033[1;37m""")

    countries = fetch_camera_sources()

    if not countries:
        print("[ERROR] Não foi possível obter os dados dos países.")
        return

    for key, value in countries.items():
        print(f'Código: ({key}) - {value["country"]} / ({value["count"]})')

    country_code = input("Código(##): ").strip().upper()
    if country_code in countries:
        get_camera_ips(country_code)
    else:
        print("[ERROR] Código de país inválido. Tente novamente.")


if __name__ == "__main__":
    main()
