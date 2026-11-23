using System;
using UnityEngine;
namespace FrameLab
{
    [Serializable] public class FrameLabStop
    {
        public string id, title, prompt, caption;
        public Vector3 position;
        public float yaw;
        public AudioClip audio;
    }
    [Serializable] public class FrameLabTour
    {
        public FrameLabStop[] rooms;
        public FrameLabStop[] studies;
    }
}
