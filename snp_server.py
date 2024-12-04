from discord_webhook import DiscordWebhook

# enter your server IP address/domain name
db_host = ""  # or "domain.com"
# database name, if you want just to connect to MySQL server, leave it empty
db_name = "eddc"
# this is the user you create
db_user = "eddc"
# user password
db_pass = ""  # eddc

webhook = DiscordWebhook(
            url="https://discord.com/api/webhooks/1267488940487610451\
            /OtpB_6s9hgczC8lQbrRuDsDTlwzRUII4OKD-uYd4vyJc5KxN-me72jdS6ISPpHFYK_lR",
            username="ExplorerChallenge")
