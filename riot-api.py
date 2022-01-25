from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv
import pandas as pd
import yaml
import os


# global variables
api_key = os.getenv('API_KEY')
watcher = LolWatcher(api_key)
# my_region = 'na1'

with open('summoners.yaml') as f:
    roster = yaml.load(f, Loader=yaml.FullLoader)


# me = watcher.summoner.by_name(my_region, 'fzpowder')


# my_puuid = me['puuid']
# print(my_puuid)
# my_matches = watcher.match.matchlist_by_puuid(region='americas', puuid = my_puuid)
# print(my_matches)

# # my_matches = watcher.match.matchlist_by_puuid(region=my_region, puuid=me['accountId'])

# # fetch last match detail
# # last_match = my_matches['matches'][0]
# match_detail = watcher.match.by_id(region='americas', match_id=my_matches[0])

# match_participants = match_detail.get('info').get('participants')

# participants = []
# for row in match_participants:
# 	participants_row = {}
# 	participants_row['champion'] = row['championName']
# 	participants_row['kills'] = row['kills']
# 	participants_row['deaths'] = row['deaths']
# 	participants.append(participants_row)

# df = pd.DataFrame(participants)
# df

# print(df)


# get player ID from discord name 
def get_summoner_aliases(discord_id):
	'''
	return all known aliases for discord user
	'''
	if roster.get(discord_id):
		return roster.get(discord_id).get('aliases')

	else:
		print('User not in summoner roster')
		return 


def get_puuid(summoner_name):
	'''
	get puuid from summoner name, return puuid of most recent account

	'''
	puuid = watcher.summoner.by_name(region='na1', summoner_name=summoner_name).get('puuid') 

	return puuid


# get last match from player ID
def get_last_match_df(puuid):
	'''
	get last match summary from puuid
	'''
	my_matches = watcher.match.matchlist_by_puuid(region='americas', puuid=puuid)
	last_match = my_matches[0]
	match_detail = watcher.match.by_id(region='americas', match_id=my_matches[0])
	game_end_timestamp = match_detail.get('info').get('gameEndTimestamp')
	match_participants = match_detail.get('info').get('participants')

	participants = []
	for row in match_participants:
		if puuid == row['puuid']:
			participants_row = {}
			participants_row['champion'] = row['championName']
			participants_row['kills'] = row['kills']
			participants_row['deaths'] = row['deaths']
			participants_row['summonerName'] = row['summonerName']
			participants_row['win'] = row['win']
			participants_row['gameEndTimestamp'] = game_end_timestamp
			participants_row['puuid'] = row['puuid']
			participants_row['puuid_self'] = puuid
			participants.append(participants_row)

	df = pd.DataFrame(participants)

	return df

# print(roster)

# print(get_last_match_df(get_puuid(get_summoner_name('fzpowder'))))


def get_last_game_summary(discord_id):

	aliases = get_summoner_aliases(discord_id)

	dfs = []

	for alias in aliases:
		puuid = get_puuid(alias)
		dfs.append(get_last_match_df(puuid))

	df = pd.concat(dfs)

	most_recent_game = df['gameEndTimestamp'].max()
	df = df[df['gameEndTimestamp'] == most_recent_game]

	out = {
		'kills': df['kills'].values[0],
		'deaths': df['deaths'].values[0],
		'champion': df['champion'].values[0],
		'win': df['win'].values[0]

	}

	return out

results = get_last_game_summary(291788732544057355)

# print(results)

print('FYI the last time this person played... they picked {0}, had {1} kills and {2} death, and {3} THE GAME'.format(results['champion'], results['kills'], results['deaths'], 'WON' if results['win'] else 'LOST'))

# print(get_summoner_aliases(291788732544057355))

# print(get_puuid('fzpowder'))

