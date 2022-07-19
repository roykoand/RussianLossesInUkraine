import re
from typing import List

import urllib3
from bs4 import BeautifulSoup


class RussianLosses:
    def __init__(
        self, url: str = "https://index.minfin.com.ua/ua/russian-invading/casualties"
    ) -> None:
        self._url = url
        self._include = [
            "Liquidated personnel",
            "Tanks",
            "Warships/Boats",
            "Aircraft/Helicopters",
            "Anti-aircraft",
            "UAV",
            "Artillery systems/MLRS",
        ]

    def parse(self):
        http = urllib3.PoolManager()
        html = http.request("GET", self._url).data.decode()
        soup = BeautifulSoup(html, "html.parser")
        casualities = soup.find("div", {"class": "casualties"})
        cleaned_categories = [
            self._replace(li.text) for li in casualities.findAll("li")
        ]
        categories = self._calculations(cleaned_categories)
        result_info = []
        for include_category in self._include:
            for category in categories:
                if include_category in category:
                    result_info.append(category)
        return ", ".join(result_info)

    @staticmethod
    def _replace(text: str) -> str:
        remove_occur = {
            "Особовий склад": "Liquidated personnel",
            "Танки": "Tanks",
            "ББМ": "ARV",
            "Літаки": "Aircraft",
            "Гелікоптери": "Helicopters",
            "БПЛА": "UAV",
            "ППО": "Anti-aircraft",
            "Крилаті ракети": "Cruise missels",
            r"Кораблі \(катери\)": "Warships/Boats",
            "Спеціальна техніка": "Special equipment",
            "Автомобілі та автоцистерни": "Vehichles/Fuel tanks",
            "Гармати": "Artillery systems",
            "РСЗВ": "MLRS",
            r", близько.*полонених": "",
            "близько ": "~",
            "осіб ": "",
            "засоби ": "",
            "\xa0": "",
            "—": ":",
        }
        for old, new in remove_occur.items():
            text = re.sub(old, new, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _calculations(cleaned: List[str]) -> List[str]:
        sum_categories = {
            "Artillery systems/MLRS": ("Artillery systems", "MLRS"),
            "Aircraft/Helicopters": ("Aircraft", "Helicopters"),
        }

        for concat_category, concat_categories in sum_categories.items():
            category_count, category_add_count = 0, 0
            for category_to_concat in concat_categories:
                for category in cleaned:
                    if re.match(category_to_concat, category):
                        matched_numbers = list(
                            filter(
                                lambda x: x,
                                re.findall("(\d+)\s?\(?\+?(\d*)\)?", category)[0],
                            )
                        )
                        category_count += int(matched_numbers[0])
                        if len(matched_numbers) == 2:
                            category_add_count += int(matched_numbers[1])
            concat_category = (
                f"{concat_category}: {category_count} (+{category_add_count})"
                if category_add_count
                else f"{concat_category}: {category_count}"
            )
            cleaned.append(concat_category)
        return cleaned
