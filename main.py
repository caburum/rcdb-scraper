import requests
import bs4
import csv

fields = ['id', 'name', 'active', 'park', 'city', 'state', 'country', 'class', 'type', 'design', 'rating', 'make', 'model']

def logError(id, block):
	print(f'\033[91mError getting {block} of {id}\033[0m')

def getCoaster(id):
	page = requests.get(f'https://rcdb.com/{id}.htm')
	soup = bs4.BeautifulSoup(page.content, 'lxml')

	result = {}
	for field in fields:
		result[field] = '' # initialize default values
	
	result['id'] = id

	# Scrape data from site

	try:
		info = soup.find(id='feature')
		result['name'] = info.find('h1')
		result['active'] = not info.find('p').text.startswith('Removed')
	except:
		logError(id, 'name/status')
		pass

	try:
		location = dict(enumerate(info.find('div').find_all('a')))
		result['park'] = location.get(0)
		result['city'] = location.get(1)
		result['state'] = location.get(2)
		result['country'] = location.get(3)
	except:
		logError(id, 'location')
		pass

	try:
		details = dict(enumerate(info.find('ul').find_all('li')))
		result['class'] = details.get(0)
		result['type'] = details.get(1)
		result['design'] = details.get(2)
		result['rating'] = details.get(3)
	except:
		logError(id, 'general')
		pass

	try:
		build = dict(enumerate(info.find(class_='scroll').find_all('a')))
		result['make'] = build.get(0)
		result['model'] = build.get(2)
	except:
		logError(id, 'make/model')
		pass

	try:
		track = soup.find_all('section')[1].find(class_='stat-tbl')
		for stat in track.find_all('tr'):
			key = stat.find('th').text.lower()
			val = stat.find('td')
	
			if key == 'elements':
				result[key] = ', '.join(set(e.text for e in val.find_all('a')))
			else:
				result[key] = val		
	except:
		logError(id, 'stats')
		pass

	# Extract text from tags
	for key, val in result.items():
		if isinstance(val, bs4.element.Tag):
			result[key] = val.text.strip()

	return result

# Take input from user
coasters = []
print('Enter rcdb coaster ID to add a coaster, blank line to finish:')
while True:
	coaster = input('')

	if coaster:
		coasters.append(getCoaster(int(coaster)))
	else:
		break

with open('output.csv', 'w') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=coasters[0].keys())
	writer.writeheader()
	writer.writerows(coasters)