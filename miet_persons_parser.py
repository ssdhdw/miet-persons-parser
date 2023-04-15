import requests
from bs4 import BeautifulSoup
import asyncio
import csv
import functools
from time import perf_counter

response = requests.get("https://miet.ru/")
headers = { "Cookie" : response.text.split('"')[1].split(";")[0]}
PAGE = "https://miet.ru/people/{}"
peoples = []

def parse_persons(persons_list):
    new_persons_list = []
    for person in persons_list:
        name = person.find("a", {"class": "people-list__item-name"}).text
        link = person.find("a", {"class": "people-list__item-name"}).get("href")
        phone = person.find("span", {"class": "people-list__item-phone"})
        if phone:
            phone = phone.text
        email = person.find("span", {"class": "people-list__item-email"})
        if email:
            email = email.find("a").text.strip()
        new_persons_list.append((name, phone, email, link))
    return(new_persons_list)

async def parse_persons_page(page):
    tic = perf_counter()
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, functools.partial(requests.get, page, headers = headers))
    response = await future
    soup = BeautifulSoup(response.text, 'html.parser')
    people_list = soup.find_all("div", {"class": "people-list__item"})
    persons = parse_persons(people_list)
    print(f"Got {len(persons)} persons from {page} in {perf_counter() - tic}")
    for i in persons:
        peoples.append(i)

async def main():
    for i in range(192, 224):
        await parse_persons_page(PAGE.format(i))
    file = open("miet persons.csv", "w+", encoding= "utf_8", newline='')
    writer = csv.writer(file)
    writer.writerow(["ФИО", "Телефон", "Почта", "Ссылка"])
    writer.writerows(peoples)
    file.close()

if __name__ == "__main__":
    asyncio.run(main())