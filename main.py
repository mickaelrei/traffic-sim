import json
import os
import os.path
# NOTE: This is used to hide pygame welcome message
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

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
    for file in files:
        print(f" - {file}")

    # Check what map the user wants to use
    print("\nChoose map by name:")
    selectedMap = input("> ").strip()
    if files.count(selectedMap) == 0:
        print("Map not found")
        return

    with open(f"./road_maps/{selectedMap}.json", "r") as f:
        # TODO: Generate nodes
        pass

    # TODO: Use selected map as input for TrafficSimulationApp:
    # - Convert lines' start/end points to world position
    # - Create map nodes from lines' start/end world position (left/right-hand sides)
    # - Each driver selects a random starting point, and a destination point as his path

    # Create and run app
    from view.simulation import TrafficSimulationApp

    app = TrafficSimulationApp(600, 600, 60)
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

    # Convert RoadLine objects to json
    jsonLines = []
    for line in app.roadLines:
        jsonLines.append(line.toJSON())

    # Save to json file
    with open(f"./road_maps/{name}.json", "w") as f:
        json.dump(jsonLines, f)


def handleOption(option: int) -> None:
    # List of options
    optionsList = [
        runSimulationApp,
        runMapEditorApp,
    ]

    # Check if option is valid
    if option == 0 or option > len(optionsList):
        return

    # Run
    optionsList[option - 1]()


def main() -> None:
    print("============================")
    print("||   Traffic Simulation   ||")
    print("============================\n")
    print("Choose an option:")
    print("[1] Run simulation")
    print("[2] Open map editor")
    print("[0] Quit\n")

    # Get user option input
    res = input("> ").strip()
    if len(res) == 0:
        # No input, return
        return

    # Handle input
    option = res[0]
    optionInt = 0
    try:
        optionInt = int(option)
    except ValueError:
        pass

    # Handle selected option
    handleOption(optionInt)


if __name__ == "__main__":
    main()
