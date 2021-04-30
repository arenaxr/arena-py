# bendy.py
#
# animate the bones of the 'izzy' GLTF model from Sketchfab
# bone names came from inspecting scene.gltf
# assumes the model 'izzy' already exists in ARENA scene 'cesium'

import arena
import random
import time
import signal

HOST = "oz.andrew.cmu.edu"
SCENE = "cesium"

bones=[
    "CC_Base_Spine01_correct_0207",
"CC_Base_Waist_correct_0206",
"CC_Base_Spine02_correct_0205",
"CC_Base_R_Clavicle_correct_0149",
"CC_Base_R_Upperarm_correct_0197",
"CC_Base_R_UpperarmTwist01_correct_0153",
"CC_Base_R_UpperarmTwist02_correct_0154",
"CC_Base_R_Forearm_correct_0155",
"CC_Base_R_Elbow_correct_0160",
"CC_Base_R_ForearmTwist01_correct_0159",
"CC_Base_R_ForearmTwist02_correct_0150",
"CC_Base_R_Hand_correct_0165",
"CC_Base_R_Finger00_correct_0147",
"CC_Base_R_Finger01_correct_0148",
"CC_Base_R_Finger02_correct_0184",
"CC_Base_R_Finger0Nub_correct_0172",
"CC_Base_R_Finger10_correct_0186",
"CC_Base_R_Finger11_correct_0171",
"CC_Base_R_Finger12_correct_0192",
"CC_Base_R_Finger1Nub_correct_0193",
"CC_Base_R_Finger20_correct_0191",
"CC_Base_R_Finger21_correct_0196",
"CC_Base_R_Finger22_correct_0158",
"CC_Base_R_Finger2Nub_correct_0156",
"CC_Base_R_Finger30_correct_0151",
"CC_Base_R_Finger31_correct_0152",
"CC_Base_R_Finger32_correct_0177",
"CC_Base_R_Finger3Nub_correct_0181",
"CC_Base_R_Finger40_correct_0157",
"CC_Base_R_Finger41_correct_0179",
"CC_Base_R_Finger42_correct_0180",
"CC_Base_R_Finger4Nub_correct_0176",
"CC_Base_L_Clavicle_correct_0167",
"CC_Base_L_Upperarm_correct_0166",
"CC_Base_L_UpperarmTwist01_correct_0168",
"CC_Base_L_UpperarmTwist02_correct_0182",
"CC_Base_L_Forearm_correct_0183",
"CC_Base_L_Elbow_correct_0178",
"CC_Base_L_ForearmTwist01_correct_0190",
"CC_Base_L_ForearmTwist02_correct_0185",
"CC_Base_L_Hand_correct_0188",
"CC_Base_L_Finger00_correct_0189",
"CC_Base_L_Finger01_correct_0164",
"CC_Base_L_Finger02_correct_0163",
"CC_Base_L_Finger0Nub_correct_0162",
"CC_Base_L_Finger10_correct_0195",
"CC_Base_L_Finger11_correct_0199",
"CC_Base_L_Finger12_correct_0200",
"CC_Base_L_Finger1Nub_correct_0161",
"CC_Base_L_Finger20_correct_0198",
"CC_Base_L_Finger21_correct_0187",
"CC_Base_L_Finger22_correct_0173",
"CC_Base_L_Finger2Nub_correct_0174",
"CC_Base_L_Finger30_correct_0201",
"CC_Base_L_Finger31_correct_0175",
"CC_Base_L_Finger32_correct_0194",
"CC_Base_L_Finger3Nub_correct_0169",
"CC_Base_L_Finger40_correct_0170",
"CC_Base_L_Finger41_correct_0202",
"CC_Base_L_Finger42_correct_0203",
"CC_Base_L_Finger4Nub_correct_0204",
"CC_Base_R_Ribs_correct_00",
"CC_Base_R_RibsNub_correct_01",
"CC_Base_R_RibsTwist_correct_02",
"CC_Base_R_Breast_correct_03",
"CC_Base_R_BreastNub_correct_04",
"CC_Base_L_Ribs_correct_05",
"CC_Base_L_RibsNub_correct_06",
"CC_Base_L_RibsTwist_correct_07",
"CC_Base_L_Breast_correct_0208",
"CC_Base_L_BreastNub_correct_0209",
"CC_Base_NeckTwist01_correct_0210",
"CC_Base_NeckTwist02_correct_0211",
"CC_Base_Head_correct_0212",
"CC_Base_HeadNub_correct_0213",
"CC_Base_R_Abdominal_correct_0214",
"CC_Base_R_AbdominalNub_correct_0215",
"CC_Base_L_Abdominal_correct_0216",
"CC_Base_L_AbdominalNub_correct_0217",
"CC_Base_Pelvis_correct_0218",
"CC_Base_R_Thigh_correct_0219",
"CC_Base_R_ThighTwist01_correct_0220",
"CC_Base_R_ThighTwist02_correct_0221",
"CC_Base_R_Calf_correct_0222",
"CC_Base_R_Knee_correct_0223",
"CC_Base_R_CalfTwist01_correct_0224",
"CC_Base_R_CalfTwist02_correct_0225",
"CC_Base_R_Foot_correct_0226",
"CC_Base_R_ToeBase_correct_0227",
"CC_Base_R_Toe00_correct_0228",
"CC_Base_R_Toe00Nub_correct_0229",
"CC_Base_R_Toe10_correct_0230",
"CC_Base_R_Toe10Nub_correct_0231",
"CC_Base_R_Toe20_correct_0232",
"CC_Base_R_Toe20Nub_correct_0233",
"CC_Base_R_Toe30_correct_0234",
"CC_Base_R_Toe30Nub_correct_0235",
"CC_Base_R_Toe40_correct_0236",
"CC_Base_R_Toe40Nub_correct_0237",
"CC_Base_R_ToeBaseShareBone_correct_0238",
"CC_Base_R_Hip0_correct_0239",
"CC_Base_R_Hip0Nub_correct_0240",
"CC_Base_L_Thigh_correct_0241",
"CC_Base_L_ThighTwist01_correct_0242",
"CC_Base_L_ThighTwist02_correct_0243",
"CC_Base_L_Calf_correct_0244",
"CC_Base_L_Knee_correct_0245",
"CC_Base_L_CalfTwist01_correct_0246",
"CC_Base_L_CalfTwist02_correct_0247",
"CC_Base_L_Foot_correct_0248",
"CC_Base_L_ToeBase_correct_0249",
"CC_Base_L_Toe40_correct_0250",
"CC_Base_L_Toe40Nub_correct_0251",
"CC_Base_L_Toe30_correct_0252",
"CC_Base_L_Toe30Nub_correct_0253",
"CC_Base_L_Toe20_correct_0254",
"CC_Base_L_Toe20Nub_correct_0255",
"CC_Base_L_Toe10_correct_0256",
"CC_Base_L_Toe10Nub_correct_0257",
"CC_Base_L_Toe00_correct_0258",
"CC_Base_L_Toe00Nub_correct_0259",
"CC_Base_L_ToeBaseShareBone_correct_0260",
"CC_Base_L_Hip0_correct_0261",
"CC_Base_L_Hip0Nub_correct_0262"]

arena.init(HOST, "realm", SCENE)

def randrot():
    r = round((random.random()/10 - 0.05), 3)
    #print(r)
    return r

def signal_handler(sig, frame):
    exit()

signal.signal(signal.SIGINT, signal_handler)
messages = []
counter = 0
while True:
    obj = scene.updateBone(
        object_id="izzy",
        rotation=(randrot(),randrot(),randrot(),1),
        bone_id = bones[random.randint(0,len(bones)-1)]
        )
    time.sleep(0.1)
exit()
