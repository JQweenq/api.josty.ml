from .timetable import timetable

timetable: Blueprint = Blueprint('timetable', __name__)

timetable.add_resourse(Reqs, '/timetable')