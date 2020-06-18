using System.Collections.Generic;
using System.IO;

namespace Aquila
{
    /// <summary>
    /// The Wavefront Object file format is not that hard to understand.
    /// Drawback is that is does not support per vertex colors.
    /// 
    /// http://www.royriggs.com/obj.html
    /// 
    /// Currently this class only supports trinagulated meshes, without any
    /// back references. Therefore this it NOT a reference implementation.
    /// Vertex positions are translated to colors, one more fancy behaviour a
    /// serious loader never would have.
    /// </summary>
    public class WavefrontObject
    {
        public static PositionNormalTexcoordVertex[] Load(string filename)
        {
            List<float> vertices = new List<float>();
            List<float> normals = new List<float>();
            List<float> texcoords = new List<float>();
            List<int> faces = new List<int>();

            // indexing starts with 1 in obj files, therefore we add an empty entry

            vertices.Add(0.0f);
            vertices.Add(0.0f);
            vertices.Add(0.0f);
            normals.Add(0.0f);
            normals.Add(0.0f);
            normals.Add(0.0f);
            texcoords.Add(0.0f);
            texcoords.Add(0.0f);

            StreamReader sr = new StreamReader(filename);
            while (!sr.EndOfStream)
            {
                string s = sr.ReadLine();
                if (s.StartsWith("#"))
                {
                    continue;
                }
                string[] parts = s.Split(' ');

                if (parts[0] == "v")
                {
                    for (int i = 1; i <= 3; i++)
                    {
                        vertices.Add(float.Parse(parts[i]));
                    }
                }
                else if (parts[0] == "vn")
                {
                    for (int i = 1; i <= 3; i++)
                    {
                        normals.Add(float.Parse(parts[i]));
                    }
                }
                else if (parts[0] == "vt")
                {
                    for (int i = 1; i <= 2; i++)
                    {
                        texcoords.Add(float.Parse(parts[i]));
                    }
                }
                else if (parts[0] == "f")
                {
                    for (int i = 1; i <= 3; i++)
                    {
                        string[] subparts = (parts[i] + "/0/0").Split('/');
                        faces.Add(int.Parse(subparts[0]));
                        faces.Add(int.Parse(subparts[2]));
                        faces.Add(int.Parse(subparts[1]));
                    }
                }

            }
            sr.Close();

            int count = faces.Count / 3;

            PositionNormalTexcoordVertex[] result = new PositionNormalTexcoordVertex[count];

            for (int i = 0; i < count; i++)
            {
                int p = faces[i * 3 + 0] * 3;
                int n = faces[i * 3 + 1] * 3;
                int t = faces[i * 3 + 2] * 2;

                Vector4 position = new Vector4();
                position.X = vertices[p + 0];
                position.Y = vertices[p + 1];
                position.Z = vertices[p + 2];
                position.W = 1.0f;

                Vector3 normal = new Vector3();
                normal.X = normals[n + 0];
                normal.Y = normals[n + 1];
                normal.Z = normals[n + 2];

                Vector2 texcoord = new Vector2();
                texcoord.X = texcoords[t + 0];
                texcoord.Y = texcoords[t + 1];

                result[i] = new PositionNormalTexcoordVertex(position, normal, texcoord);
            }

            return result;
        }
    }
}
