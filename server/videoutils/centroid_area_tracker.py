#elaborated from https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/

# import the necessary packages
from collections import OrderedDict
import math
from threading import Lock

class CentroidAreaTracker():
	def __init__(self, max_disappeared_frames=3):
		# initialize the next unique object ID along with two ordered
		# dictionaries used to keep track of mapping a given object
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.next_object_id = 0
		self.registered_objects = OrderedDict()
		self.disappeared_objects = OrderedDict()
		self.update_lock = Lock()

		# store the number of maximum consecutive frames a given
		# object is allowed to be marked as "disappeared" until we
		# need to deregister the object from tracking
		self.max_disappeared_frames = max_disappeared_frames

	def __register(self, object_descriptor):
		# when registering an object we use the next available object
		# ID to store the centroid
		self.registered_objects[self.next_object_id] = object_descriptor
		self.disappeared_objects[self.next_object_id] = 0
		self.next_object_id += 1

	def __deregister(self, object_id):
		# to deregister an object ID we delete the object ID from
		# both of our respective dictionaries
		del self.registered_objects[object_id]
		del self.disappeared_objects[object_id]

	def update(self, frame_object_descriptors): #frame objects should be tuples of a centre location (x, y) and an area
		with self.update_lock:
			# check to see if the list of input objects is empty
			if len(frame_object_descriptors) == 0:
				# loop over any existing tracked objects and mark them
				# as disappeared
				deregister_keys = []
				for object_id in self.disappeared_objects.keys():
					self.disappeared_objects[object_id] += 1

					# if we have reached a maximum number of consecutive
					# frames where a given object has been marked as
					# missing, deregister it
					if self.disappeared_objects[object_id] > self.max_disappeared_frames:
						deregister_keys.append(object_id)
				for object_id in deregister_keys:
					self.__deregister(object_id)
				# return early as there are no centroids or tracking info
				# to update
				return self.registered_objects

			# if we are currently not tracking any objects take the input
			# centroids and register each of them
			if len(self.registered_objects) == 0:
				for i in range(0, len(frame_object_descriptors)):
					self.__register(frame_object_descriptors[i])

			# otherwise, are are currently tracking objects so we need to
			# try to match the centroids of the input objects to centroids of the existing objects
			else:
				# grab the set of object IDs and corresponding centroids
				registered_object_ids = list(self.registered_objects.keys())
				registered_object_descriptors = list(self.registered_objects.values())

				#populate list of possible correspondences and difference index (distance multiplied by area discrepancy)
				registered_object_index = 0
				differences = []
				for registered_object_descriptor in registered_object_descriptors:
					frame_object_index = 0
					for frame_object_descriptor in frame_object_descriptors:
						area_ratio = max(registered_object_descriptor[2], frame_object_descriptor[2])/min(registered_object_descriptor[2], frame_object_descriptor[2])
						# if (area_ratio >= 2):
						# 	print('area ratio >2')
						# if(area_ratio<2): #if area difference is more than 2x - do not even consider correspondence
						difference = math.sqrt(
							(registered_object_descriptor[0]-frame_object_descriptor[0])**2 +
							(registered_object_descriptor[1]-frame_object_descriptor[1])**2
						) * area_ratio
						differences.append((difference, registered_object_index, frame_object_index))
						frame_object_index += 1
					registered_object_index += 1

				differences.sort(key=lambda tup: tup[0])

				#greedy algo to find correspondecies
				matched_registered_object_indices = set()
				matched_frame_object_indices = set()
				for (difference, registered_object_index, frame_object_index) in differences:
					if registered_object_index in matched_registered_object_indices \
							or frame_object_index in matched_frame_object_indices:
						continue
					#we call it a match
					object_id = registered_object_ids[registered_object_index]
					self.registered_objects[object_id] = frame_object_descriptors[frame_object_index]
					self.disappeared_objects[object_id] = 0
					matched_registered_object_indices.add(registered_object_index)
					matched_frame_object_indices.add(frame_object_index)


				#increase disappeared counter / deregister active objects without correspondencies
				deregister_keys = []
				for registered_object_index in range(len(registered_object_ids)):
					if registered_object_index in matched_registered_object_indices: continue
					object_id = registered_object_ids[registered_object_index]
					self.disappeared_objects[object_id] += 1

					# check to see if the number of consecutive
					# frames the object has been marked "disappeared"
					# for warrants deregistering the object
					if self.disappeared_objects[object_id] > self.max_disappeared_frames:
						deregister_keys.append(object_id)

				for object_id in deregister_keys:
					self.__deregister(object_id)

				#register new objects
				for frame_object_index in range(len(frame_object_descriptors)):
					if frame_object_index in matched_frame_object_indices: continue
					self.__register(frame_object_descriptors[frame_object_index])

			# return the set of trackable objects
			return self.registered_objects