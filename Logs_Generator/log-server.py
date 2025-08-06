from concurrent import futures
import logging
from shared.logger import getLogger
import random
import grpc
from LogsGen import logs_pb2
from LogsGen import logs_pb2_grpc
from google.protobuf import empty_pb2

logger = getLogger("logs-generator-service")

class LogsService(logs_pb2_grpc.LogsServiceServicer):
    def logs(self, request, context):
        """
        gRPC method to trigger log generation.
        """
        logger.info("Received gRPC request to generate logs...")
        self.generate_logs()
        return empty_pb2.Empty()


    
    def generate_logs(self):
        """
        Endpoint to generate logs for testing purposes.
        """
        functions = [self.ZeroDivisionError, self.SyntaxError, self.random_no_generator]   
        logger.info("Generating logs...")
        for _ in range(10):
            try:
               func = random.choice(functions)
               func()
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
    

    def ZeroDivisionError(self):
        """
        Function to raise a ZeroDivisionError for testing purposes.
        """
        random_number = random.randint(0, 5)
        try:
            res = 10 / random_number
            logger.info(f"Generated random number: {random_number}, result: {res}")
        except ZeroDivisionError as e:
            logger.error(f"ZeroDivisionError raised: {str(e)}")

    def SyntaxError(self):
                """
                Function to raise a SyntaxError for testing purposes.
                """
                eval("x === x")
                logger.error("SyntaxError raised")

    def random_no_generator(self):
        if random.randint(0,3) < 1:
            logger.error("Random error occurred")


 

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logs_pb2_grpc.add_LogsServiceServicer_to_server(LogsService(), server)
    server.add_insecure_port('[::]:5000')
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()