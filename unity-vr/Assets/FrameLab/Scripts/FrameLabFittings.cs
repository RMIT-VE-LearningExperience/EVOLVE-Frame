using System;
using System.Linq;
using UnityEngine;

namespace FrameLab
{
    public class FrameLabFittings : MonoBehaviour
    {
        [Serializable] public class Group
        {
            public string label;
            public Renderer[] surfaces;
            public bool shown = true;
        }
        public Group[] groups;
        public bool AnyHidden => Array.Exists(groups, group => !group.shown);
        public Renderer[] Surfaces => groups.SelectMany(group => group.surfaces).ToArray();
        public void Set(int index, bool shown)
        {
            groups[index].shown = shown;
            FrameLabSession.SetSurfaces(groups[index].surfaces, shown);
        }
        public void SetAll(bool shown)
        {
            for (int i = 0; i < groups.Length; i++) Set(i, shown);
        }
    }
}
