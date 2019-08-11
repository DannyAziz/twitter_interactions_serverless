from chalice import Chalice, Response
from requests_html import HTMLSession

app = Chalice(app_name='twitter_interactions')

twitter_url = 'https://mobile.twitter.com/search?q=from%3A{}%20to%3A{}'


@app.route('/fetch-interactions')
def index():
    request = app.current_request
    if "from_user" not in request.query_params:
        return Response(
            body={"error": "No from_user supplied"},
            status_code=400
        )
    if "to_user" not in request.query_params:
        return Response(
            body={"error": "No to_user supplied"},
            status_code=400
        )

    url = twitter_url.format(request.query_params["from_user"], request.query_params["to_user"])
    session = HTMLSession()
    r = session.get(
        url,
        headers={
            'cookie': 'm5=off'
        }
    )

    ids = []
    load_more = True
    timeline = r.html.find(".timeline", first=True)
    if timeline:
        tweets = timeline.find("table")
        while load_more:
            for tweet in tweets:
                ids.append(
                    tweet.find(".timestamp", first=True).find("a", first=True).attrs["name"].replace("tweet_", "")
                )
            load_more_container = r.html.find(".w-button-more", first=True)
            if load_more_container:
                load_more_link = load_more_container.find("a", first=True).attrs["href"]
                load_more_url = "https://mobile.twitter.com" + load_more_link
                r = session.get(
                    load_more_url,
                    headers={
                        'cookie': 'm5=off'
                    }
                )
                timeline = r.html.find(".timeline", first=True)
                if not timeline:
                    load_more = False
            else:
                load_more = False
        return ids
    return {"error": True}
