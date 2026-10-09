// Reproducible source-build smoke test. Uses only the public RoR scripting API.
float elapsed = 0;
int lastSecond = -1;
bool initialized = false;
bool overlayOpen = true;
bool screenshot1 = false;
bool screenshot2 = false;
bool screenshot3 = false;
vector3 initialPosition;
float maxSpeed = 0;
void main() { game.log("BUILD_PROOF script loaded; source e85535569102b6251849af574026984e3213b3f4"); }
void frameStep(float dt)
{
    BeamClass@ truck = game.getCurrentTruck();
    if (truck is null) return;
    if (!initialized) {
        initialPosition = truck.getPosition();
        EngineClass@ engine = truck.getEngine();
        if (engine !is null) { engine.startEngine(); engine.setAutoMode(SimGearboxMode::SEMI_AUTO); engine.setGear(1); }
        if (truck.getParkingBrake()) truck.parkingbrakeToggle();
        game.log("BUILD_PROOF vehicle=" + truck.getTruckFileName() + " nodes=" + truck.getNodeCount());
        initialized = true;
    }
    elapsed += dt;
    float throttle = elapsed > 5 && elapsed < 29 ? 0.85f : 0.0f;
    truck.setEventSimulatedValue(EV_TRUCK_ACCELERATE, throttle);
    truck.setEventSimulatedValue(EV_TRUCK_BRAKE, elapsed > 29 ? 0.6f : 0.0f);
    vector3 p = truck.getPosition();
    float speed = truck.getWheelSpeed() * 3.6f;
    if (speed > maxSpeed) maxSpeed = speed;
    float distance = (p - initialPosition).length();
    int second = int(elapsed);
    if (second != lastSecond) {
        lastSecond = second;
        game.log("BUILD_PROOF sample t="+second+" x="+p.x+" y="+p.y+" z="+p.z+" kph="+speed+" displacement_m="+distance);
    }
    ImGui::SetNextWindowPos(vector2(20,20), ImGuiCond_Always);
    ImGui::SetNextWindowSize(vector2(455,155));
    if (ImGui::Begin("Source build verification", overlayOpen, ImGuiWindowFlags_NoResize)) {
        ImGui::Text("bert-systems/rigs-of-rods-trials | e855355");
        ImGui::Text("Compiled locally with MSVC 19.44 | Release x64");
        ImGui::Text("Terrain: simple2 | Vehicle: Daf Semi truck");
        ImGui::Text("Elapsed: " + second + " s | Wheel speed: " + speed + " km/h");
        ImGui::Text("Displacement: " + distance + " m | Nodes: " + truck.getNodeCount());
        ImGui::Text(throttle > 0 ? "CONTROL: throttle 85 percent" : (elapsed > 29 ? "CONTROL: braking" : "CONTROL: idle"));
        ImGui::End();
    }
    if (!screenshot1 && elapsed > 3) { screenshot1=true; game.pushMessage(MSG_APP_SCREENSHOT_REQUESTED, null); }
    if (!screenshot2 && elapsed > 16) { screenshot2=true; game.pushMessage(MSG_APP_SCREENSHOT_REQUESTED, null); }
    if (!screenshot3 && elapsed > 32) { screenshot3=true; game.pushMessage(MSG_APP_SCREENSHOT_REQUESTED, null); }
    if (elapsed > 36) {
        game.log("BUILD_PROOF complete elapsed_s="+elapsed+" displacement_m="+distance+" maximum_wheel_kph="+maxSpeed);
        truck.clearEventSimulatedValues();
        game.quitGame();
    }
}

