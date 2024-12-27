from NotesTableManager import NotesTableManager as ntm
from IntervalChecker import IntervalChecker

tableManager=ntm()
notes_table=tableManager.get_notes_table()

intervalChecker=IntervalChecker(notes_table)
print(intervalChecker.get_notes_for_repetition())
