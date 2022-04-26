from distutils.log import error
from tokenize import String
from atlassian import Bitbucket #atlassian-python-api
from atlassian import Confluence #atlassian-python-api
from datetime import datetime
import argparse

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

def getLabelCategory(bitbucket, repo_slug):
    labels = bitbucket.get_repo_labels(project_key, repo_slug)
    for label in labels['values']:
        if isCategory(label['name']):
            return label['name']
    return None


def categorize(bitbucket, repo_slug):
    category = getRepoNameCategory(repo_slug)
    if category is None:
        category = getLabelCategory(bitbucket, repo_slug)
    if category is None:
        category = "other"
    return category

def createHeading():
    text = 'h3. These are our repositories at date: '
    text += datetime.today().strftime('%Y-%m-%d') + '\n  '
    return text

def createLists(repos):
    text = ''
    for category in repos:
        text += 'h3. ' + category.capitalize() + '\n  '
        for repo in repos[category]:
            text += '[' + repo + '|https://diva.teliacompany.net/bitbucket/projects/DC-MYBDBE/repos/' + repo + '/browse]\n  '
    return text

def getFromBitbucket(args):
    bitbucket = Bitbucket(url= 'https://diva.teliacompany.net/bitbucket',
                username= args.username,
                password= args.password)

    repos = bitbucket.repo_list(project_key)

    teamRepos = {}
    for repo in repos:
        if repo['description'].lower().startswith(args.team.lower()):
            category = categorize(bitbucket, repo['slug'])
            if category not in teamRepos:
                teamRepos[category] = []
            
            teamRepos[category].append(repo['slug'])

    return teamRepos

def writeConfluence(args, repos):

    confluence = Confluence(url= 'https://diva.teliacompany.net/confluence',
                username= args.username,
                password= args.password)

    space = 'mybusiness'
    page_title = args.team.capitalize() + ' Backend repos'    
    if confluence.page_exists(space=space, title=page_title):
        page_id = confluence.get_page_id(space='mybusiness', title=page_title)
        page = confluence.get_page_by_id(page_id, expand="body.view")
        text = createHeading()
        text += createLists(repos)

        confluence.update_page(page_id, page_title, text, type='page', representation='wiki', minor_edit=False)
    else:
        print("Could not find page " + page_title + " in MyBusiness, please create one in appropriate location")

parser = argparse.ArgumentParser(description='Get data from Bitbucket and update Confluence')
parser.add_argument('-u', dest='username', required=True, help='username for both bitbucket and confluence')
parser.add_argument('-p', dest='password', required=True, help='password for both bitbucket and confluence')
parser.add_argument('-t', dest='team', required=True, help='Team name, used for bitbucket and confluence structure')

args = parser.parse_args()

repos = getFromBitbucket(args= args)
writeConfluence(args=args, repos=repos)

