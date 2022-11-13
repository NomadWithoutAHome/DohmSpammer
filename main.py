import requests as req
import click as c
import time
import json


# create a command using click that sends a message to a webhook url in a loop but check if the webhook is valid first with delay and how many times to send the message to the webhook waiting if rate limited
@c.command()  # this is a command
@c.option('--url', '-u', required=True,
          help='The webhook url to send the message to.')  # required=True means that the option is required
@c.option('--message', '-m', required=True,
          help='The message to send to the webhook.')  # required=True means that the option is required
@c.option('--delay', '-d', default=0,
          help='The delay between each message sent to the webhook.')  # default=0 means that the delay is 0 seconds
@c.option('--count', '-c', default=1, required=True,
          help='The amount of times to send the message to the webhook.')  # required=True because if you don't specify a count then it will send the message once and then exit
def send_message(url, message, delay, count):  # the function that sends the message to the webhook
    for i in range(int(count)):  # loop the amount of times specified by the user
        rep = req.post(url, json={"content": message})  # send the message to the webhook
        if rep.status_code in [401]:  # if the status code is 401 then the webhook is invalid
            c.echo(
                'Invalid webhook url, please check the webhook url and try again!')  # print this if the webhook is invalid
            break  # break the loop
        c.echo(f'times sent: {i + 1}')  # print how many times the message has been sent
        if rep.status_code == 429:  # if the status code is 429 then the webhook is rate limited
            wait = json.loads(rep.content.decode("utf-8"))  # get the wait time from the response
            retry = (int(wait[
                             "retry_after"]) / 1000) + 0.15  # add 0.15 seconds to the retry_after time to make sure it doesn't get rate limited again
            c.echo(
                f"Rate limited! Waiting {retry} seconds...")  # if rate limited then wait the amount of time given by the response
            time.sleep(retry)  # wait for the retry_after time
            c.echo("Rate limit lifted!")  # if rate limited then wait the amount of time and then send the message again
            rep = req.post(url, json={"content": message})  # send the message again
            c.echo(f'Current Status Code: {rep.status_code}')  # print the status code
        else:
            c.echo(f'Current Status Code: {rep.status_code}')
        time.sleep(int(delay))
    # if option is true then get the webhook info
    rep = req.post(url)
    if rep.status_code not in [401]:
        if c.confirm('Do you want to get the webhook info?'):
            get_webhook_info(url)


# Get the webhook info and save it to json file
def get_webhook_info(url):
    rep = req.get(url)  # get the webhook info
    if rep.status_code in [200, 201]:  # if the status code is 200 or 201 then the webhook is valid

        # gather info
        name = rep.json()['name']
        id = rep.json()['id']
        token = rep.json()['token']
        avatar = rep.json()['avatar']
        channel_id = rep.json()['channel_id']
        guild_id = rep.json()['guild_id']
        hook_url = 'https://discord.com/api/webhooks/' + id + '/' + token

        # put info into a nested dictionary
        valid = {'Dohm Spammer': {name: {
            'id': id,
            'token': token,
            'avatar': avatar,
            'channel_id': channel_id,
            'guild_id': guild_id,
            'hook_url': hook_url
        }
        }
        }
        # try and save the info to a json file
        try:
            with open('webhook_info.json', 'w') as f:  # change the name of the file to whatever you want
                json.dump(valid, f, indent=4)  # indent=4 makes it look nice
            c.echo('Webhook info saved to json file!')  # if successful
        except:
            c.echo('Failed to save webhook info to json file!')  # if failed to save to json file then print this
    else:
        c.echo('Invalid webhook url!')  # if the webhook is invalid then print invalid webhook url


# run the command
if __name__ == '__main__':
    send_message()

# @c.command()
# @c.option('--url', '-u', required=True, help='The webhook url to send the message to.')
# @c.option('--message', '-m', required=True, help='The message to send to the webhook.')
# @c.option('--delay', '-d', default=0, help='The delay between each message sent to the webhook.')
# @c.option('--count', '-c', default=1, required=True, help='The amount of times to send the message to the webhook.')
# def send_message(url, message, delay, count):
#     # check if the webhook is valid
#     try:
#         rep = req.get(url, {"name": "application/json"})
#         rep.raise_for_status()
#
#         webhook_info = rep.json()
#         print(f"Webhook {url} is valid!")
#         print(f"Webhook name: {webhook_info['name']}")
#         print(f"Webhook id: {webhook_info['id']}")
#         print(f"Webhook token: {webhook_info['token']}")
#         print(f"Webhook avatar: {webhook_info['avatar']}")
#         print(f"Webhook channel_id: {webhook_info['channel_id']}")
#         print(f"Webhook guild_id: {webhook_info['guild_id']}")
#         print(f"Webhook url: https://discord.com/api/webhooks/{webhook_info['id']}/{webhook_info['token']}")
#
#         # send the message to the webhook
#         for i in range(int(count)):
#             rep = req.post(url, json={"content": message})
#             rep.raise_for_status()
#             print(f"Message sent to {url}!")
#
#             time.sleep(int(delay))
#
#     except req.exceptions.HTTPError as err:
#         c.echo(err)
#
#
# if __name__ == '__main__':
#     send_message()
#
