import os
from typing import Optional
from atproto import Client, Session, SessionEvent
# based on https://atproto.blue/en/latest/atproto_client/auth.html


class BskyAuth:
    def get_session(self) -> Optional[str]:
        """Check if session token exists yet.

        Returns:
            Optional[str]: str if token exists, None if it does not.
        """
        try:
            with open('session.txt', encoding='UTF-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
    

    def save_session(self, session_token: str) -> None:
        with open('session.txt', 'w', encoding='UTF-8') as f:
            f.write(session_token)

    
    def on_session_change(self, event: SessionEvent, session: Session) -> None:
        print('Session changed:', event, repr(session))
        if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
            print('Saving session change')
            self.save_session(session.export())


    def init_client(self, ) -> Client:
        client = Client()
        client.on_session_change(self.on_session_change)

        session_token = self.get_session()
        if session_token:
            print('Reusing session')
            client.login(session_string=session_token)
        else:
            print('Creating new session')
            client.login(os.environ['BSKY_HANDLE'],
                         os.environ['BSKY_PASSWORD'])
            
        return client