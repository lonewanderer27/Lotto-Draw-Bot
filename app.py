from typing import Union
from fastapi import FastAPI, Query
import uvicorn
from PCSOLotto import PCSOLotto
from pprint import pprint
import textwrap
from datetime import datetime

app = FastAPI()
days_list = [
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Sun'
]
results_unavailable = 'Sorry, results are not available yet. Please check again later.'

params_desc = {
    'start_date':
    """
    Date to start searching.
    Format has to be YYYY/MM/DD
    """,

    'end_date':
    """
    Date to end searching.
    Format has to be YYYY/MM/DD
    """,

    'days':
    """
    Days to select.
    """,

    'games':
    """
    Lotto games to search.
    """,

    'peso_sign':
    """
    To prefix a peso sign in the jackpot, or not.
    """
}

tags_metadata = [
    {
        'name': 'latest',
        'description': 'Retrieve lotto results from 3 days prior up to today.'
    },
    {
        'name': 'today',
        'description': 'Retrieve lotto results today.'
    },
    {
        'name': 'yesterday',
        'description': 'Retrieve lotto results from yesterday.'
    }
]


def split_message(json: dict, text: str, n: int = 9):
    if n == 9:
        # makes sure that all the message is split evenly across 9 messages
        n = round(len(text) / 9)

    text_blocks = textwrap.wrap(
        text,
        width=n,
        break_long_words=False,
        break_on_hyphens=False,
        drop_whitespace=True,
        replace_whitespace=False
    )

    for text_block in text_blocks:
        print(len(text_block))
        json['messages'].append({'text': f'{text_block}'},)
    return json


@app.get("/")
async def index():
    return {
        'message': 'Hello Chatfuel and World!'
    }


@app.get("/api/custom")
async def custom(
    start_date: str = Query(description=params_desc['start_date'],
                            example="2022/08/01"),
    end_date: str = Query(description=params_desc['end_date'],
                          example="2022/08/12"),
    days: Union[list[str], None] = Query(default=None,
                                   description=params_desc['days'],
                                   example="Sun, Mon, Tue ..."),
    games: Union[list[str], None] = Query(default=None,
                                    description=params_desc['games'],
                                    example="EZ2, 6/42, 6Digit etc..."),
    peso_sign: bool = Query(default=True,
                            description=params_desc['peso_sign']),
):
    lotto = PCSOLotto()
    try:
        datetime.strptime(start_date, '%Y/%m/%d')
    except Exception as e:
        print(e)
        return {
            'success': False,
            'message': 'Invalid start_date parameter',
            'detail': "Cannot parse start_date. Make sure it uses the format: YYYY/MM/DD"
        }

    try:
        datetime.strptime(end_date, '%Y/%m/%d')
    except Exception as e:
        print(e)
        return {
            'success': False,
            'message': 'Invalid end_date -arameter',
            'detail': "Cannot parse start_date. Make sure it uses the format: YYYY/MM/DD"
        }

    print(f"Days: {days}")
    if days is not None:
        for day in days:
            print(day)
            if day not in days_list:
                print(f"{day} not in days_list")
                return {
                    'success': False,
                    'message': f"Invalid '{day}' day in days parameter",
                    'detail': f"Only allowed days: Mon, Tue, Wed, Thu, Fri, Sat, Sun. '{day}' is not in the list."
                }

    results = lotto.results(
        start_date=start_date,
        end_date=end_date,
        days=days,
        games=games,
        peso_sign=peso_sign
    )

    return {
            'message': 'ok',
            'results': results
        }


@app.get("/api/latest")
async def latest(
    games: Union[list[str], None] = Query(default=None,
                                    description=params_desc['games'],
                                    example="EZ2, 6/42, 6Digit etc..."),
    peso_sign: bool = Query(default=True,
                            description=params_desc['peso_sign']),
    chatfuel: bool = False
):
    lotto = PCSOLotto()
    lotto_result_list_str = ""

    if chatfuel:
        json = {'messages': []}

        results = lotto.results_default_pcso(
            games=games,
            peso_sign=peso_sign
        )

        if len(results) > 0:
            lotto_result_list_str = "\n\n".join(lotto.result_list_str)
            print(lotto_result_list_str)

            response = split_message(json, lotto_result_list_str, 650)

        else:

            response = {
                'success': False,
                'message': results_unavailable,
                'messages': [
                    {'text': results_unavailable}
                ]
            }

        pprint(response, indent=2)
        return response

    else:
        results = lotto.results_default_pcso(
            games=games,
            peso_sign=peso_sign
        )
        pprint(results, indent=2)

        if len(results) > 0:
            return {
                'success': True,
                'message': 'ok',
                'results': results
            }
        else:
            return {
                'success': False,
                'message': results_unavailable
            }


@app.get("/api/today")
async def today(
    games: Union[list[str], None] = Query(default=None,
                                    description=params_desc['games'],
                                    example="EZ2, 6/42, 6Digit etc..."),
    peso_sign: bool = Query(default=True,
                            description=params_desc['peso_sign']),
    chatfuel: bool = False
):
    lotto = PCSOLotto()
    lotto_result_list_str = ""
    if chatfuel:

        json = {'messages': []}

        results = lotto.results_today(
            games=games,
            peso_sign=peso_sign
        )

        if len(results) > 0:
            lotto_result_list_str = "\n\n".join(lotto.result_list_str)
            response = split_message(json, lotto_result_list_str, 500)

        else:
            response = {
                'success': False,
                'message': results_unavailable,
                'messages': [
                    {'text': results_unavailable}
                ]
            }

        pprint(response, indent=2)
        return response

    else:
        results = lotto.results_today(
            games=games,
            peso_sign=peso_sign
        )
        pprint(results, indent=2)

        if len(results) > 0:
            return {
                'success': True,
                'message': 'ok',
                'results': results
            }
        else:
            return {
                'success': False,
                'message': results_unavailable
            }


@app.get("/api/yesterday")
async def yesterday(
    games: Union[list[str], None] = Query(default=None,
                                    description=params_desc['games'],
                                    example="EZ2, 6/42, 6Digit etc..."),
    peso_sign: bool = Query(default=True,
                            description=params_desc['peso_sign']),
    chatfuel: bool = False
):
    lotto = PCSOLotto()
    lotto_result_list_str = ""
    if chatfuel:

        json = {'messages': []}

        results = lotto.results_yesterday(
            games=games,
            peso_sign=peso_sign
        )

        if len(results) > 0:
            lotto_result_list_str = "\n\n".join(lotto.result_list_str)
            print(lotto_result_list_str)

            response = split_message(json, lotto_result_list_str, 500)
        else:
            response = {
                'success': False,
                'message': results_unavailable,
                'messages': [
                    {'text': results_unavailable}
                ]
            }

        pprint(response, indent=2)
        return response

    else:
        results = lotto.results_yesterday(
            games=games,
            peso_sign=peso_sign
        )
        pprint(results, indent=2)

        if len(results) > 0:
            return {
                'success': True,
                'message': 'ok',
                'results': results
            }
        else:
            return {
                'success': False,
                'message': results_unavailable
            }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0")
