#!/usr/bin/python -u

import time
import xmlrpclib
import datetime

class InvalidTicket (Exception):
    def __init__ (self):
        self.value = 'Invalid Ticket ID'
        
    def __str__ (self):
        return repr(self.value)
        
class TicketAPI (object):
    def __init__ (self, username, passwd):
        self.server_url = 'https://%s:%s@code.djangoproject.com/login/rpc'  % (username, passwd)
        self.server_proxy = xmlrpclib.ServerProxy(self.server_url)
        
    def create (self, summary, description, attrs={}):
        """Creates a new ticket and returns its Ticket ID"""
        
        return self.server_proxy.ticket.create(summary, description, attrs)
        
    def put_attachment (self, ticket_id, data, filename=None, description=None):
        ts = time.gmtime()
        if filename is None:
            filename = time.strftime("%Y%m%d_%H%M%S.txt", ts)
            
        if description is None:
            description = time.strftime("Posted: %a, %d %b %Y %H:%M:%S +0000", ts)
            
        if self.get_ticket(ticket_id):
            b64_data = xmlrpclib.Binary(data)
            return self.server_proxy.ticket.putAttachment(ticket_id, filename, description, b64_data, False)
            
        raise InvalidTicket()
        
    def get_ticket (self, ticket_id):
        try:
            ticket = self.server_proxy.ticket.get(ticket_id)
            
        except xmlrpclib.Fault as err:
            if err.faultCode == 404:
                return None
                
            raise
            
        else:
            return ticket[0]
            
    def changelog_test (self, ticket_id):
        """Return change log for past 24 hours"""
        
        dt = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        return self.get_changelog(ticket_id, dt)
        
    def get_changelog (self, ticket_id, ts=None):
        """Returns a list of changes, if time stamp is given, will return only
        changes equal to or after date time.  Pretty sure date time should be UTC 
        but don't quote me on that.  @pizzapanther
        """
        
        if self.get_ticket(ticket_id):
            changelog = self.server_proxy.ticket.changeLog(ticket_id)
            
            if ts:
                ret = []
                for change in changelog:
                    if change[0] >= ts:
                       ret.append(change)
                       
                return ret
                
            return changelog
            
        return None
        