from atlassian import Bitbucket #atlassian-python-api
from atlassian import Confluence #atlassian-python-api
from datetime import datetime

project_key = 'DC-MYBDBE'

def isCategory(type):
    if type == 'service':
        return True
    elif type == 'starter':
        return True
    elif type == 'scripts':
        return True

def getRepoNameCategory(repo_slug):
    category = repo_slug.split('-')[-1]
    if isCategory(category):
        return category
    return None

def getLabelCategory(repo_slug):
    labels = bitbucket.get_repo_labels(project_key, repo_slug)
    for label in labels['values']:
        if isCategory(label['name']):
            return label['name']
    return None


def categorize(repo_slug):
    category = getRepoNameCategory(repo_slug)
    if category is None:
        category = getLabelCategory(repo_slug)
    if category is None:
        category = "other"
    return category

def createHeading():
    text = 'Instructions of how the backend repositories work and how to test them in the GUI.\n  '
    text += 'h3. These are our repositories by the date '
    text += datetime.today().strftime('%Y-%m-%d') + '\n  '
    return text

def createLists(repos):
    text = ''
    for category in repos:
        text += 'h3. ' + category.capitalize() + '\n  '
        for repo in repos[category]:
            text += repo + '\n  '
    return text

bitbucket = Bitbucket(url= 'https://diva.teliacompany.net/bitbucket',
            username= 'username',
            password= 'password')

repos = bitbucket.repo_list(project_key)

tengilrepos = {}
for repo in repos:
    if repo['description'].startswith('Tengil'):
        category = categorize(repo['slug'])
        if category not in tengilrepos:
            tengilrepos[category] = []
        
        tengilrepos[category].append(repo['slug'])

confluence = Confluence(url= 'https://diva.teliacompany.net/confluence',
            username= 'username',
            password= 'password')

page_id = confluence.get_page_id(space='mybusiness', title='Tengil Backend repos')
page = confluence.get_page_by_id(page_id, expand="body.view")

text = createHeading()
text += createLists(tengilrepos)

#confluence.update_page(page_id, 'Tengil Backend repos', text, type='page', representation='wiki', minor_edit=False)
