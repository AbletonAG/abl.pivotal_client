import logging

import urllib, urllib2
from xml.dom import minidom
from xml.dom.minidom import Node

logger = logging.getLogger(__name__)


class PivotalClient(object):
    """Interacts with Pivotal via the Pivotal API."""
    STORY_TYPE_RELEASE = 'release'
    STORY_TYPE_BUG = 'bug'
    TYPES_WITHOUT_POINTS = (STORY_TYPE_RELEASE, STORY_TYPE_BUG)


    def __init__(self, token):
        self.token = token


    def _get_node_data(self, node, tag_name):
        tags = node.getElementsByTagName(tag_name)
        if tags:
            first_occurence = tags[0].firstChild
        else:
            logger.debug("""\
Didn't find any tags named %s in node %s.""" % (tag_name, node))
            return u''

        try:
            return first_occurence.data
        except AttributeError:
            return None


    def _extract_project_data(self, project):
        """
        Extract data for a single project.
        """
        project_data = dict()
        root_elements = [x for x in project.childNodes if x.nodeType == Node.ELEMENT_NODE]

        project_data['id'] =  [x for x in root_elements if x.tagName == 'id'][0].childNodes[0].nodeValue
        project_data['name'] = [x for x in root_elements if x.tagName == 'name'][0].childNodes[0].nodeValue

        return project_data


    def _extract_story_data(self, story):
        """
        Extract data for a single story.

        Some story types are not estimated and therefore have no
        points. In such cases hard-coded values are set for the
        `points` key. See TYPES_WITHOUT_POINTS.

        :param story: a story element
        :type story: DOM element

        :returns: relevant data about a story
        :rtype: dictionary
        """
        story_id = self._get_node_data(story, 'id')
        title = self._get_node_data(story, 'name')
        description = self._get_node_data(story, 'description')
        labels = self._get_node_data(story, 'labels')
        story_type = self._get_node_data(story, 'story_type')
        accepted = self._get_node_data(story, 'accepted_at')
        points = None

        if story_type not in PivotalClient.TYPES_WITHOUT_POINTS:
            points = self._get_node_data(story, 'estimate')

        return dict(story_id=story_id,
                    story_type=story_type,
                    title=title,
                    description=description,
                    labels=labels,
                    points=points,
                    accepted=accepted)


    def _send_request(self, project_id=None, command=None, url_params=None):
        """
        Make an HTTP request to Pivotal and parse the response.

        :param command: API command to perform
        :type command: string

        :param params: (optional) GET parameters to append to the
        action
        :type params: list

        :return: the parsed request
        """
        base_url = 'https://www.pivotaltracker.com/services/v3'
        extra_url = []
        extra_params = []

        if project_id:
            extra_url.append('projects')
            extra_url.append(project_id)

        if command:
            extra_url.append(command)

        if url_params:
            extra_params = urllib.urlencode(url_params).replace('+', '%20') # Pivotal doesn't like +

        url = '%s/%s%s' % (base_url,
                           '/'.join(extra_url) or '',
                           ('?' + extra_params) if extra_params else '')

        req = urllib2.Request(url, None, {'X-TrackerToken': '%s' % self.token})

        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError:
            print "Error opening %s:" % url
            raise

        return minidom.parseString(response.read())


    def get_story(self, story_id, project_id):
        """
        Get stories by ID.

        :param story_id: the id of a story to fetch.
        :type story_id: a string

        :returns: interesting data about stories
        :rtype: a dictionary
        """
        command = 'stories/%s' % story_id
        data = self._send_request(
            project_id=project_id,
            command=command,
            )

        s = data.getElementsByTagName('story')
        if len(s) == 0:
            return None
        else:
            return self._extract_story_data(s[0])


    def get_stories(self, project_id, **filters):
        """
        Get stories by arbitrary filters.

        :returns: interesting data about stories
        :rtype: a list of dictionaries
        """
        command = 'stories'
        url_params = {}
        if filters:
            url_params['filter'] = ' '.join('{}:{}'.format(key, value) for key, value in filters.iteritems())
        data = self._send_request(
            project_id=project_id,
            command=command,
            url_params=url_params,
            )

        return [self._extract_story_data(s) for s in data.getElementsByTagName('story')]


    def get_stories_by_id(self, ids, project_id):
        """
        Get stories by ID.

        :param ids: one or several ids of stories to fetch.
        :type ids: a list of strings

        :returns: interesting data about stories
        :rtype: a list of dictionaries
        """
        return self.get_stories(id=','.join(ids))


    def get_current_iteration(self, project_id):
        """
        Return story data for all unfinished stories in the current
        iteration.
        """
        command = 'iterations/current'
        data = self._send_request(
            project_id=project_id,
            command=command,
            )

        story_data = [self._extract_story_data(s) for s in data.getElementsByTagName('story')]
        return [s for s in story_data if s['story_type'].lower() in ('feature', 'bug', 'chore', 'release')]


    def get_projects(self):
        """
        Get all Pivotal projects.
        """
        res = self._send_request(command='projects')

        return [self._extract_project_data(p) for p in res.getElementsByTagName('project')]
