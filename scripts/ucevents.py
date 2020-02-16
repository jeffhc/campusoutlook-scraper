import requests
from bs4 import BeautifulSoup
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


url = 'https://events.uchicago.edu/cal/main/showMain.rdo'
base_url = 'https://events.uchicago.edu'
gql_server = 'https://ucevents.herokuapp.com/'

client = Client(
  transport=RequestsHTTPTransport(url=gql_server, use_json=True),
  fetch_schema_from_transport=True,
)
mutation = gql('''
mutation {
  createEvent(
    name: "jeff test",
    description:"test", 
    timeobj: {start: 1521930600, end: 1521940600 }, 
    tags: ["concert", "billie", "eilish"],
    event_photo_url: "test") {
    name
    description
    time{start, end}
    tags
  }
}
''')

query = gql("""
{
  events {
    name
  }
}
""")




#######################
#     DAY EVENTS
#######################

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

events = soup.find_all('table')[1].find_all('tbody')[0].find_all('tr')
parsed_events = []

for event in events:
  parsed = {}
  data = event.find_all('td')
  if len(data) > 1:
    parsed['time'] = " ".join(data[0].get_text().split())
    info = data[1].get_text('|')
    info = " ".join(info.split())
    parsed['name'] = info.split('|')[1]
    parsed['location'] = info.split('|')[3]
    parsed['link'] = data[1].a['href']
    parsed_events.append(parsed)


##############################################
#     GET INFO FROM SINGLE EVENT
##############################################

#   Returns a JSON of form { time, location, description, tags, name, link}

def get_event_info(event_link):
  event_page = requests.get(event_link)
  soup = BeautifulSoup(event_page.content, 'html.parser')
  data = soup.find('table').get_text('|')
  parsed = ' '.join(data.split())
  all_items = [i for i in parsed.split('|') if i.strip()]

  meta = ['When:','Where:','Description:','Cost:','Contact:','Tag:','Notes:']
  our_meta = ['time','location','description','','','tags','']
  parsed_event_info = {}

  for i, m in enumerate(meta):
    if not i == len(meta)-1:
      if meta[i] in all_items and meta[i+1] in all_items:
        start = all_items.index(meta[i])
        end = all_items.index(meta[i+1])
        repieced = ' '.join(all_items[start+1:end])
        if our_meta[i]:
          parsed_event_info[our_meta[i]] = repieced
  
  title_part = soup.find(id='maincontent')
  parsed_event_info['name'] = title_part.parent.find('h1').get_text()

  if 'tags' in parsed_event_info:
    parsed_event_info['tags'] = str(parsed_event_info['tags'].split(',')).replace("'", '"')
    

  parsed_event_info['link'] = event_link


  for key in parsed_event_info:
    if not key == 'tags':
      parsed_event_info[key] = parsed_event_info[key].replace('"', '')
    

  return parsed_event_info



for event in parsed_events[1:]:
  info = get_event_info( base_url + event['link'] )
  if not 'All Events' in info['name']:
    mutation = gql('''
    mutation {
      createEvent(
        name: "%s",
        description: "%s", 
        location: "%s",
        timeobj: {start: 1521930600, end: 1521940600 }, 
        tags: %s,
        event_photo_url: "test") {
        name
        description
        time{start, end}
        tags
      }
    }
    '''  % ( info.get('name', ''), info.get('description', ''), info.get('location', ''), info.get('tags', '[\"test\"]') ) )
    print(client.execute(mutation))