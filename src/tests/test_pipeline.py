from unittest import TestCase

from hypergol.pipeline import Pipeline


class TestDataset(TestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    # TODO(Laszlo): mock pool and check if the correct number of threads created and all jobs executed
    def test_pipeline(self):
        self.assertEqual(True, True)
        # pipeline = Pipeline(
        #     tasks=[
        #         mockSource,
        #         mockTask1,
        #         mockTask2
        #     ]
        # )
        # pipeline.run(threads=4)
        # print(mockPool)
