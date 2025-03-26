import sqlalchemy as sql # time to lock in for the job 💯


# oh man this about to look crazy 
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


'''

I store my messages in my database so that when a user disconnects, then reconnects and they get my messages
what is important is the time stamps so we see when they logged off and get all messages that weren't sent since that time 
logic can be like if(isOnline) then send message else store message in database
when user logs back in, we check the database for messages and send them to the user
we can also store the messages in a hash table with the key being the user and the value being a list of messages for constant time access XD 


USER MESSAGES DB
messageID: int -> autoincrement
destination: string -> 127.0.0.1 (_ if recieving message)
source: string -> 127.0.0.1 ( _ if sending messsage)
message: string -> "Hello"
timeStamp: timeStamp UTC -> "12:00"
isRead: bool -> False

OR 2 DIFFERENT TABLES FOR RECIEVED AND SENT ?

ids are either guids or autoincremented integers

guid good because the user can't guess the next message id and can't read other messages but not best performance (good for identity) 

autoincremented integers are good because they are faster and you can do a lot more with them but they are predictable


'''
# TODO: set up the db base, engine, and session 
# TODO: set up tables using classes and __tablename__ and __repr__ and create the tables if they don't exist 
# TODO: deliver_pending_messages function to get all messages that haven't been read and send them to the user
# TODO: store_inbound_message function in handle_peer to store inbound message in the database
# TODO: add offline_peers to broadcast function to store messages in the database if the user is offline and remove them from peers
# TODO: store_outbound_message function to store message being sent to the offline peer
# TODO: add logic to delivering pending messages when conneting to new person 

class Base(DeclarativeBase):
    pass

class OutboundMessages(Base):
    __tablename__ = "outbound_messages"

    id : Mapped[int] = mapped_column(sql.Integer, primary_key=True)
    destination: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    timeStamp: Mapped[str] = mapped_column(sql.DateTime)
    isRead: Mapped[bool] = mapped_column(sql.Boolean)

    def __repr__(self):
        return f"OutboundMessage(id={self.id!r}, destination={self.destination!r}, source={self.source!r}, message={self.message!r}, timeStamp={self.timeStamp!r}, isRead={self.isRead!r})"

class InboundMessages(Base):
    __tablename__ = "inbound_messages"

    id : Mapped[int] = mapped_column(sql.Integer, primary_key=True)
    destination: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    timeStamp: Mapped[str] = mapped_column(sql.DateTime)
    isRead: Mapped[bool] = mapped_column(sql.Boolean)

    def __repr__(self):
        return f"InboundMessage(id={self.id!r}, destination={self.destination!r}, source={self.source!r}, message={self.message!r}, timeStamp={self.timeStamp!r}, isRead={self.isRead!r})"


engine = create_engine("sqlite:///messages.db")
Session = sql.orm.sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def store_inbound_messages(source, message):
    """Store inbound message in the database."""
    with Session() as session:
        outbound = OutboundMessages(
            destination=s.gethostbyname(s.gethostname()),
            source=source,
            message=message,
            timeStamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            isRead=False
        )
        session.add(outbound)
        session.commit()
        
def get_inbound_messages():
    """Get all messages that haven't been read."""
    session = Session()
    stmr = (
        select(OutboundMessages)
    )
    messages = session.execute(stmr).fetchall()
    session.close()
    return messages

