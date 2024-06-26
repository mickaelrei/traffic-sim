import json
import os
import os.path
# NOTE: This is used to hide pygame welcome message
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

# Maximum cars in simulation
MAX_CARS_SIMULATION = 20

# Gets user bool input (yes/no)
def getUserBoolInput(prompt: str):
    print(f"{prompt} [Y/n]")
    res = input("> ").strip().lower()

    return len(res) == 0 or res[0] == "y"

# Runs a simulation app with the selected map
def runSimulationApp() -> None:
    # List all available maps
    files = os.listdir("./road_maps")
    if len(files) == 0:
        print(
            "[WARNING]: No road map files found on default folder "
            "\"traffic-sim/road_maps\". Create one with the"
            " editor and save it to a file to use it on a simulation",
        )
        return

    # Filter files
    for i in range(len(files) - 1, -1, -1):
        file = files[i]
        if len(file) < 5:
            # Not enough length for .json extension
            files.remove(file)

        # Check for json extension
        if file[-5:].lower() != ".json":
            # No json extension
            files.remove(file)

        # Valid json, remove extension
        files[i] = file[:-5]

    print("\nAvailable maps:")
    for i, file in enumerate(files):
        print(f"[{i + 1}] {file}")

    # Check what map the user wants to use
    print("\nChoose map by number:")
    index = input("> ").strip()
    try:
        index = int(index)
        if index <= 0 or index > len(files):
            print("\nInvalid number")
            return
    except ValueError:
        return

    # How many cars in the simulation
    print(f"\nHow many cars in the simulation? [1-{MAX_CARS_SIMULATION}]")
    numCars = input("> ").strip()
    try:
        numCars = int(numCars)
        if numCars <= 0 or numCars > MAX_CARS_SIMULATION:
            print("\nInvalid input: Number out of range")
            return
    except ValueError:
        print("Invalid input: Not a number")
        return

    # Create and run app
    from view.simulation import TrafficSimulationApp

    app = TrafficSimulationApp(
        600,
        600,
        numCars=numCars,
        roadMapFilePath=f"./road_maps/{files[index - 1]}.json",
        fps=60,
    )
    app.run()

# Runs map editor app, possibly saving a map to a file
def runMapEditorApp() -> None:
    from view.map_editor import MapEditorApp

    # TODO: Check if user wants to start editor from an existing road map

    # Create and run app
    app = MapEditorApp(600, 600, 60)
    app.run()

    # Check if user wants to save map
    while not app.isRoadMapValid():
        continueEdit = getUserBoolInput(
            "\nRoad map is invalid.\nWant to continue editing?")
        if not continueEdit:
            return

        # Rerun app
        app.run()

    # Road is valid, check if want to save
    save = getUserBoolInput("\nSave road map?")
    if not save:
        return

    # Get map name
    print("\nMap name:")
    name = input("> ").strip()
    while len(name) == 0:
        print("Name can't be empty.\n")
        name = input("> ").strip()

    # Convert RoadLine objects to json
    jsonLines = []
    for line in app.roadLines:
        jsonLines.append(line.toJSON())

    # Save to json file
    with open(f"./road_maps/{name}.json", "w") as f:
        json.dump(jsonLines, f, indent=4)

# Runs a map loader with the selected map
def runMapLoadingTestApp() -> None:
    # List all available maps
    files = os.listdir("./road_maps")
    if len(files) == 0:
        print(
            "[WARNING]: No road map files found on default folder "
            "\"traffic-sim/road_maps\". Create one with the"
            " editor and save it to a file to use it on a simulation",
        )
        return

    # Filter files
    for i in range(len(files) - 1, -1, -1):
        file = files[i]
        if len(file) < 5:
            # Not enough length for .json extension
            files.remove(file)

        # Check for json extension
        if file[-5:].lower() != ".json":
            # No json extension
            files.remove(file)

        # Valid json, remove extension
        files[i] = file[:-5]

    print("\nAvailable maps:")
    for i, file in enumerate(files):
        print(f"[{i + 1}] {file}")

    # Check what map the user wants to use
    print("\nChoose map by number:")
    index = input("> ").strip()
    try:
        index = int(index)
        if index <= 0 or index > len(files):
            print("\nInvalid number")
            return
    except ValueError:
        return

    from view.short_path_algo import ShortPathAlgorithmApp

    app = ShortPathAlgorithmApp(
        600,
        600,
        60,
        roadMapFilePath=f"./road_maps/{files[index - 1]}.json",
    )
    app.run()

def handleOption(option: int) -> None:
    # List of options
    optionsList = [
        runSimulationApp,
        runMapEditorApp,
        runMapLoadingTestApp,
    ]

    # Check if option is valid
    if option == 0 or option > len(optionsList):
        return

    # Run
    optionsList[option - 1]()


def main() -> None:
    # Check if road maps dir exists
    if not os.path.exists("./road_maps"):
        os.mkdir("./road_maps")

    print("============================")
    print("||   Traffic Simulation   ||")
    print("============================\n")
    print("Choose an option:")
    print("[1] Run simulation")
    print("[2] Open map editor")
    print("[3] Run map loading test")
    print("[0] Quit\n")

    # Get user option input
    res = input("> ").strip()
    if len(res) == 0:
        # No input, return
        return

    # Handle input
    optionInt = 0
    try:
        optionInt = int(res)
    except ValueError:
        pass

    # Handle selected option
    handleOption(optionInt)


if __name__ == "__main__":
    main()
