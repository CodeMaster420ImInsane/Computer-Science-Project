using System;
using System.IO;

namespace CSProject
{
    class Program
    {
        Dictionary<int, List<double>> SMA = new Dictionary<int, List<double>>(); //Creating a list to calculate the Simple Moving Averages
        public class Data //Creating variables to add as headings on a table
        {
            String dateTime;
            double closeAvg, lowAvg, highAvg, openAvg;
            Boolean buySuccess, sellSuccess;
            List<double> SMAAvgs = new List<double>();
            public Data(String dateTime, double closeAvg, double lowAvg, double highAvg, double openAvg) //Constructor for all the variables in Data
            {
                this.dateTime = dateTime;
                this.closeAvg = closeAvg;
                this.lowAvg = lowAvg;
                this.highAvg = highAvg;
                this.openAvg = openAvg;
            }
            public void AddSMA(double SMAAvg)
            {
                SMAAvgs.Add(SMAAvg);
            }
            public void setBuySuccess(Boolean buySuccess)
            {
                this.buySuccess = buySuccess;
            }
            public void setSellSuccess(Boolean sellSuccess)
            {
                this.sellSuccess = sellSuccess;
            }
            public string printLine() // Prints every line of data after calculations of SMAs are made
            {
                return dateTime + "\t" + closeAvg + "\t" + lowAvg + "\t" + highAvg + "\t" + openAvg + String.Join("\t", SMAAvgs);
            }

        }

        public static void Main(String[] args)
        {
            new Program(new int[] { 5, 50, 100 }, 0.8f); //Creating an SMA with period 5, 50, and 100
        }
        private double addAvg(double closeAvg, int numPeriods)
        {
            List<double> SMAavg = SMA[numPeriods]; //Makes a list which produces 3 lines
            SMAavg.Add(closeAvg);
            if (SMAavg.Count > numPeriods)
            {
                SMAavg.RemoveAt(0);
            }
            double total = 0;
            for (int i = 0; i < SMAavg.Count; i++)
            {
                total += SMAavg[i];
            }
            return total / SMAavg.Count;
        }
        public Program(int[] numPeriods, float testFraction)
        {
            String fileName = "C:\\Users\\craig\\Desktop\\DownloadHist1minGBPNZD_5yr.txt";
            //String fileName = "C:\\Users\\craig\\Desktop\\smallTest.txt";
            foreach (int i in numPeriods)
            {
                SMA.Add(i, new List<double>());
            }
            String line = null;
            int noOfLines = 0;
            //get file line count
            StreamReader sr = new StreamReader(fileName);
            try
            {
                // file lines count
                do
                {
                    line = sr.ReadLine();
                    noOfLines++;

                } while (line != null);
                sr.Close();


                int frame = (int)(noOfLines * testFraction);
                foreach (String run in new String[] { "Train", "Test" }) //Using ternary operators to split data 80-20
                {
                    int minLineCount = run.Equals("Train") ? 1 : frame; //start at second line: ignore headers
                    int maxLineCount = run.Equals("Train") ? frame : noOfLines;
                    sr = new StreamReader(fileName);
                    int lineCount = 0;
                    List<String> writeFileLines = new List<String>();
                    writeFileLines.Add("Date Time\tClose Average\tLow Average\tHigh Average\tOpen Average\tSMA" + String.Join("\tSMA", numPeriods));

                    string prevHour = null;
                    Data prevLine = null;
                    do
                    {
                        line = sr.ReadLine();
                        if (line != null && lineCount >= minLineCount && lineCount < maxLineCount)
                        {
                            string[] results = line.Split("\t"); //Makes a string array of every category (split by a tab)
                            string hour = results[0].Substring(11, 2);
                            prevHour = prevHour == null ? hour : prevHour; // setting the first line only to current hour
                            double closeAvg = (double.Parse(results[results.Length - 2]) + double.Parse(results[results.Length - 1])) / 2; //These 4 lines are just taking the averages of 2 categories each
                            double lowAvg = (double.Parse(results[results.Length - 4]) + double.Parse(results[results.Length - 3])) / 2;
                            double highAvg = (double.Parse(results[results.Length - 6]) + double.Parse(results[results.Length - 5])) / 2;
                            double openAvg = (double.Parse(results[results.Length - 8]) + double.Parse(results[results.Length - 7])) / 2;
                            Data lineData = new Data(results[0], closeAvg, lowAvg, highAvg, openAvg);
                            foreach (int j in numPeriods)
                            {
                                double SMAwindowAvg = addAvg(closeAvg, j);
                                lineData.AddSMA(SMAwindowAvg);
                            }
                            if (!prevHour.Equals(hour)) //taking every hour rather than minute
                            {
                                Console.WriteLine("New hour: " + prevLine.printLine());

                                if (prevLine != null) // only deal with whole hours of data
                                {
                                    //final print
                                    // Console.WriteLine(lineData.printLine());
                                    writeFileLines.Add(prevLine.printLine()); // adding the last line of the hour
                                }

                            }

                            //  Console.WriteLine(results[results.Length - 2] + ", " + results[results.Length - 1]);  


                            prevHour = hour;
                            prevLine = lineData;

                        }
                        lineCount++;
                    }
                    while (line != null);

                    sr.Close();
                    Console.WriteLine("Line count " + writeFileLines.Count);
                    File.WriteAllLines(run + "writeLines.txt", writeFileLines.ToArray()); //Compiles 2 files: TrainwriteLines and TestwriteLines with the data split
                    Console.WriteLine(run + " done");
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("Exception: " + e);
            }
            finally
            {
                Console.WriteLine("Check line"); //Final check
            }
        }


    }
}
