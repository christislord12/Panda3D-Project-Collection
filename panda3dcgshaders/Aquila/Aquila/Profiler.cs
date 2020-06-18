using System.Collections.Generic;

namespace Aquila
{
    public class Profiler
    {
        static Profiler instance = new Profiler();

        private Profiler()
        {
            //
        }

        public static Profiler Instance
        {
            get { return instance; }
        }

        List<Timer> timers = new List<Timer>();

        public void Reset()
        {
            foreach (Timer timer in timers)
            {
                timer.Reset();
            }
        }

        public string Overview()
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder(1024);
            foreach (Timer timer in timers)
            {
                sb.Append(string.Format("{0}: {1:0.0} ms\n", timer.Name, timer.MilliSeconds));
            }
            return sb.ToString();
        }

        public Timer CreateTimer(string name)
        {
            Timer timer = new Timer(name);
            timers.Add(timer);
            return timer;
        }
    }

    public class Timer
    {
        System.Diagnostics.Stopwatch sw = new System.Diagnostics.Stopwatch();
        string name;

        public Timer(string name)
        {
            this.name = name;
        }

        public string Name
        {
            get { return this.name; }
        }

        public void Start()
        {
            this.sw.Start();
        }

        public void Stop()
        {
            this.sw.Stop();
        }

        public void Reset()
        {
            this.sw.Reset();
        }

        public float MilliSeconds
        {
            get { return (float)this.sw.Elapsed.TotalMilliseconds; }
        }
    }
}
