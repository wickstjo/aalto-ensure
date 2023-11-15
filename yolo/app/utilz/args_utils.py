import argparse

def producer_args():

    # INITIALIZE THE PARSER
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        default="mini",
        help="Path to the dataset. You can give multiple paths separated by space.",
    )

    parser.add_argument(
        "--verbose",
        action='store_true',
        default=False,
        help="Enables more descriptive printing for easier debugging.",
    )

    parser.add_argument(
        "--kafka",
        type=str,
        default="localhost:10001,localhost:10002,localhost:10003",
        help="Kafka bootstrap server and port. You can list multiple in the same string.",
    )

    parser.add_argument(
        "--max_frames",
        type=int,
        default=-1,
        help="Stop reading data after this limit is reached. Default is unlimited.",
    )

    parser.add_argument(
        "--max_vehicles",
        type=int,
        default=-1,
        help="Limit maximum amount of sensors that are processed each frame. Maximum of day-night cycle is computed from"
            "this value. Default is unlimited.",
    )

    parser.add_argument(
        "--fps",
        type=float,
        default=5,
        help="Target dataset frames per second that will be fed to Kafka.",
    )

    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Repeat all given datasets n times.",
    )

    parser.add_argument(
        "--buffer",
        type=int,
        default=1000,
        help="Size of the disk IO buffer in dataset frames.",
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Initial delay (seconds) before starting to feed data to Kafka. Useful for preloading data and delaying"
            "the start of the experiment.",
    )

    # FINALLY, RETURN THE PARSED ARGS
    print('PRODUCER ARGS LOADED')
    return parser.parse_args()

def consumer_args():

    # INITIALIZE THE PARSER
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s",
        "--kafka",
        type=str,
        default="localhost:10001,localhost:10002,localhost:10003",
        help="Kafka bootstrap server and port",
    )

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="custom-750k",
        help="What type of model the consumer should use",
    )

    # FINALLY, RETURN THE PARSED ARGS
    print('CONSUMER ARGS LOADED')
    return parser.parse_args()