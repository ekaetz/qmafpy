from .actor import Actor


class SubsriptionMgr(Actor):
	"""This module handles subscriptions
	Data can be published under a topic (a key name for the data)
	Published data can be subscribed to.  The subscriber needs to provide a queue and task name where the data will be sent.
	"""

	def __init__(self, log_level=0):
		self.published_data = {}
		"""
		Each published item is stored as:
			key	= topic
			value = data_object
		"""
		self.subscriptions = {}
		"""
		Each subscription item is stored as a dictionary under each topic:
			key	= topic
			value = dictionary of subscribers.  
				key = subscription ID
					value = (destination queue name, task_method)
					When this topic is published, the enqueued item will contain (task_method, data_object)
		"""	
		self.name = "subscription"
		super().__init__(self.name, log_level=log_level)
		self.subs_ids_cnt = {}  # Contains a count of each time a dup id used.  A new ID is generated using this int.

	def _publish(self, topic:str, data):
		"""Data is published under a topic (an identifier)
		Any subscribers to the data will be sent the data.
		"""
		self.log(f"Publish Event topic={topic} data={data}", 5)
		with self.lock:
			#Store
			self.published_data[topic] = data
			#Service Subscriptions
			self._check_subs(topic)

	def _check_subs(self, topic:str):
		if topic in self.subscriptions:
			for subscription in self.subscriptions[topic].values():
				# value = (dest_q, task, data_only)
				dest_q, task_method, attributes = subscription
				data = self.published_data[topic]
				self.enqueue(dest_q, task_method, topic, attributes, data)

	def add_subscription(self, topic:str, dest_q:str, task_method, attributes=None, subs_id=None):
		"""Data is subscribed by providing the topic, a queue and task name for where to send the data.
		"""
		self.log(f"Subscribe Event topic={topic} dest_q={dest_q} task_method={task_method}", 5)
		if subs_id is None:
			subs_id = str(dest_q)
			if subs_id in self.subs_ids_cnt:
				subs_id_original = subs_id
				subs_id = subs_id + "_" + str(self.subs_ids_cnt[subs_id])
				self.subs_ids_cnt[subs_id_original] += 1
			else:
				self.subs_ids_cnt[subs_id] = 1
		with self.lock:
			self.log(f"Subscription for {topic} sourceID={subs_id} task={task_method}", 3)
			if not topic in self.subscriptions:
				self.subscriptions[topic] = {}
			self.subscriptions[topic][subs_id] = (dest_q,task_method, attributes)

	def get_data(self, topic:str, default_value=None):
		"""The last published data under the specified topic will be returned.
		If no data for the topic exists, then the defaultValue will be returned."""
		return self.published_data.get(topic, default_value)

	def unsubscribe(self, topic, subs_id):
		with self.lock:
			if topic in self.subscriptions and subs_id in self.subscriptions[topic]:
				del self.subscriptions[topic][subs_id]

	def reset(self):
		"""This method clears any stored published data and subscriptions.
		"""
		self.published_data = {}
		self.subscriptions = {}
	