import lldb
import threading

class EventListener():
	listener = None
	event_queue = None

	def __init__(self, listener, event_queue):
		super().__init__()

		self.listener = listener
		self.event_queue = event_queue

	def starListener(self):
		threading.Thread(target=self.lldb_event_thread, args=(self.listener, self.event_queue), daemon=True).start()

	def lldb_event_thread(self, listener, event_queue):
		while True:
			event = lldb.SBEvent()
			if self.listener.WaitForEvent(1, event):
				self.event_queue.put(event)

