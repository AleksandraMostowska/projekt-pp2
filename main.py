import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas

def get_stars(opinion):
    stars = opinion.find(class_="score-marker score-marker--s")
    width = stars.get("style")
    return float(re.search("\d+\.\d+", width).group()) / 20

def get_opinion_and_purchase_date(opinion):
    opinion_time = opinion.find(class_="user-post__published").find("time", datetime=True)
    purchase_time = opinion_time.find_next("time", datetime=True)
    opinion_datetime = datetime.strptime(opinion_time["datetime"], "%Y-%m-%d %H:%M:%S")
    purchase_datetime = datetime.strptime(purchase_time["datetime"], "%Y-%m-%d %H:%M:%S") if purchase_time else ""
    return opinion_datetime, purchase_datetime

def get_likes_and_dislikes(opinion):
    likes_data = opinion.find(class_="vote-yes js_product-review-vote js_vote-yes")
    likes = int(likes_data.find("span").text) if likes_data else 0
    dislikes_data = opinion.find(class_="vote-no js_product-review-vote js_vote-no")
    dislikes = int(dislikes_data.find("span").text) if likes_data else 0
    return likes, dislikes

def get_pros_and_cons(opinion):
    pros, cons = [], []
    cols = opinion.find_all(class_="review-feature__col")
    for col in cols:
        items = col.find_all(class_="review-feature__item")
        if col.find(class_="review-feature__title review-feature__title--positives"):
            pros = [i.text.strip() for i in items]
        elif col.find(class_="review-feature__title review-feature__title--negatives"):
            cons = [i.text.strip() for i in items]
    
    return pros, cons


def get_product_reviews(prod_id: str) -> list[str]:
    page_number = 1
    all_reviews_data = []

    while True:
        url = f"https://www.ceneo.pl/{prod_id}/opinie-{page_number}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        opinions = soup.find_all(class_="js_product-review")

    
        for opinion in opinions:
            recom = opinion.find(class_="user-post__author-recomendation")
            op_and_pur_time = get_opinion_and_purchase_date(opinion)
            likes_and_dislikes = get_likes_and_dislikes(opinion)
            content = opinion.find(class_="user-post__text")
            pros_and_cons = get_pros_and_cons(opinion)
            opinion_data = {
                "ID": opinion.get("data-entry-id"),
                "author": opinion.find(class_="user-post__author-name").text.strip(),
                "recomendation": recom.text.strip() if recom else "",
                "stars": get_stars(opinion),
                "opinion_time": op_and_pur_time[0],
                "purchase_time": op_and_pur_time[1],
                "likes": likes_and_dislikes[0],
                "dislikes": likes_and_dislikes[1],
                "content": content.text.strip() if content else "",
                "pros": pros_and_cons[0],
                "cons": pros_and_cons[1],
            }

            all_reviews_data.append(opinion_data)

        

        has_next_page = soup.find(class_="pagination__item pagination__next")
        if has_next_page:
            page_number += 1
        else:
            break

    return all_reviews_data


def main() -> None:
    prod_id = input("Enter product id: ")
    opinions = get_product_reviews(prod_id)
    # print(opinions)

    pd = pandas.DataFrame(opinions)
    # print(pd)

    pd.to_csv("opinions.csv", index=False)


if __name__ == '__main__':
    main()

