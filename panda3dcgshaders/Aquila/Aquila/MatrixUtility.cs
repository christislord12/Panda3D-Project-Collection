namespace Aquila
{
    public class MatrixUtility
    {
        // http://www.opengl.org/sdk/docs/man/xhtml/glTranslate.xml
        public static Matrix4 Translate(Vector3 vector)
        {
            Matrix4 matrix = new Matrix4();

            float x = vector.X;
            float y = vector.Y;
            float z = vector.Z;

            matrix.E00 = 1.0f; matrix.E01 = 0.0f; matrix.E02 = 0.0f; matrix.E03 = x;
            matrix.E10 = 0.0f; matrix.E11 = 1.0f; matrix.E12 = 0.0f; matrix.E13 = y;
            matrix.E20 = 0.0f; matrix.E21 = 0.0f; matrix.E22 = 1.0f; matrix.E23 = z;
            matrix.E30 = 0.0f; matrix.E31 = 0.0f; matrix.E32 = 0.0f; matrix.E33 = 1.0f;

            return matrix;
        }

        // http://www.opengl.org/sdk/docs/man/xhtml/glRotate.xml
        public static Matrix4 Rotate(float radians, Vector3 vector)
        {
            Matrix4 matrix = new Matrix4();

            float x = vector.X;
            float y = vector.Y;
            float z = vector.Z;

            float c = Math.Cos(radians);
            float s = Math.Sin(radians);

            matrix.E00 = x * x * (1.0f - c) + c;
            matrix.E01 = x * y * (1.0f - c) - z * s;
            matrix.E02 = x * z * (1.0f - c) + y * s;
            matrix.E03 = 0.0f;

            matrix.E10 = y * x * (1.0f - c) + z * s;
            matrix.E11 = y * y * (1.0f - c) + c;
            matrix.E12 = y * z * (1.0f - c) - x * s;
            matrix.E13 = 0.0f;

            matrix.E20 = x * z * (1.0f - c) - y * s;
            matrix.E21 = y * z * (1.0f - c) + x * s;
            matrix.E22 = z * z * (1.0f - c) + c;
            matrix.E23 = 0.0f;

            matrix.E30 = 0.0f;
            matrix.E31 = 0.0f;
            matrix.E32 = 0.0f;
            matrix.E33 = 1.0f;

            return matrix;
        }

        // http://www.opengl.org/sdk/docs/man/xhtml/gluLookAt.xml
        public static Matrix4 LookAt(Vector3 eye, Vector3 center, Vector3 up)
        {
            Matrix4 matrix = new Matrix4();

            Vector3 f = new Vector3(center.X - eye.X, center.Y - eye.Y, center.Z - eye.Z);
            f.Normalize();

            up.Normalize();

            Vector3 s = Vector3.Cross(f, up);
            Vector3 u = Vector3.Cross(s, f);

            matrix.E00 = s.X;
            matrix.E01 = s.Y;
            matrix.E02 = s.Z;
            matrix.E03 = 0.0f;

            matrix.E10 = u.X;
            matrix.E11 = u.Y;
            matrix.E12 = u.Z;
            matrix.E13 = 0.0f;

            matrix.E20 = -f.X;
            matrix.E21 = -f.Y;
            matrix.E22 = -f.Z;
            matrix.E23 = 0.0f;

            matrix.E30 = 0.0f;
            matrix.E31 = 0.0f;
            matrix.E32 = 0.0f;
            matrix.E33 = 1.0f;

            return matrix;
        }

        // http://www.opengl.org/sdk/docs/man/xhtml/gluPerspective.xml
        public static Matrix4 Perspective(float fieldOfView, float aspectRatio, float zNear, float zFar)
        {
            Matrix4 matrix = new Matrix4();

            float f = Math.Cot(fieldOfView / 2.0f);

            matrix.E00 = f / aspectRatio;
            matrix.E01 = 0.0f;
            matrix.E02 = 0.0f;
            matrix.E03 = 0.0f;

            matrix.E10 = 0.0f;
            matrix.E11 = f;
            matrix.E12 = 0.0f;
            matrix.E13 = 0.0f;

            matrix.E20 = 0.0f;
            matrix.E21 = 0.0f;
            matrix.E22 = (zFar + zNear) / (zNear - zFar);
            matrix.E23 = (2 * zFar * zNear) / (zNear - zFar);

            matrix.E30 = 0.0f;
            matrix.E31 = 0.0f;
            matrix.E32 = -1.0f;
            matrix.E33 = 0.0f;

            return matrix;
        }
    }
}
