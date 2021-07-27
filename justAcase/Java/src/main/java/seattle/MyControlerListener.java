//-------------------------------------------------
// The function is used to control simulation monitors to obtain:
// 1. system-wide 
//	1) average distance
//	2) average travel time
//	3) total distance
//	4) total volumes
// 2. link-level
//	1) link-level volumes, grouped by linkId and/or 
//	2) hour of the day
// 3. vehicle-level
// 	1) travel time of each vehicle and of each hour
//	2) traveling distance of each vehicle
//
// Content:
// 1. every time when an iteration starts, the following monitors are activated:
//	1) avgD: system-wide average distance and total distance  
//	2) avgTT: system-wide average travel time
//	3) depCounter: system-wide total volumes
//	4) indiVol: link-level volumes, grouped by linkId and/or hour of the day
//	4) indiTT: travel time of each vehicle and of each hour
//	6) indiD: traveling distance of each vehicle
//
// @ Author: Ohay Angah (oangah@uw.edu)
// 2021.07.10
//-------------------------------------------------

package seattle;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.network.Link;
import org.matsim.api.core.v01.population.Person;
import org.matsim.core.controler.events.IterationEndsEvent;
import org.matsim.core.controler.events.IterationStartsEvent;
import org.matsim.core.controler.listener.IterationEndsListener;
import org.matsim.core.controler.listener.IterationStartsListener;
import org.matsim.vehicles.Vehicle;

public class MyControlerListener implements IterationStartsListener, IterationEndsListener {
	private	Map<Id<Person>,		ArrayList<Double>>	travelTimes			=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Id<Link>>>	travelRoutes	=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Id<Link>>>	linkEnterIds	=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Id<Link>>>	linkExitIds		=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Double>>	linkEnterTimes		=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Double>>	linkExitTimes		=	new	HashMap<>();
	private Map<Id<Vehicle>,	Integer>				activityCnts		=	new HashMap<>();
	private MyEventHandler	myEventHandler = new MyEventHandler(travelTimes, travelRoutes, linkEnterIds,	linkExitIds, linkEnterTimes, linkExitTimes, activityCnts);
	private String	outFolder;
	private final double	iterAnalysis	=	1.; // want to output the analysis at every iterAnalysis
	
	public MyControlerListener(String outFolder) {
		this.outFolder = outFolder;
	}
	
	private static void writeTravelTtime(Map<Id<Person>, ArrayList<Double>> outMap, String outFname) throws IOException 
	{
		// new file object
        File file = new File(outFname);
  
        BufferedWriter bf = null;
  
        try {
  
            // create new BufferedWriter for the output file
            bf = new BufferedWriter(new FileWriter(file));
  
            // iterate map entries
            for (Entry<Id<Person>, ArrayList<Double>> entry :
            	outMap.entrySet()) {
 
            	bf.write(entry.getKey().toString() + ":");
            	
            	int size = entry.getValue().size();
            	if (size==0) {
            		bf.write("\n");
            	}
            	for (int ix=0; ix<size; ix++) {
            		bf.write("\t");
            		bf.write(entry.getValue().get(ix).toString());
            	}
            	bf.write("\n");
            }
  
            bf.flush();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        finally {
  
            try {
  
                // always close the writer
                bf.close();
            }
            catch (Exception e) {
            }
        }
	}
	
	private static void writeTimes(Map<Id<Vehicle>,	ArrayList<Double>> outMap, String outFname) throws IOException 
	{
		// new file object
        File file = new File(outFname);
  
        BufferedWriter bf = null;
  
        try {
  
            // create new BufferedWriter for the output file
            bf = new BufferedWriter(new FileWriter(file));
  
            // iterate map entries
            for (Entry<Id<Vehicle>, ArrayList<Double>> entry :
            	outMap.entrySet()) {
 
            	bf.write(entry.getKey().toString() + ":");
            	
            	int size = entry.getValue().size();
            	if (size==0) {
            		bf.write("\n");
            	}
            	for (int ix=0; ix<size; ix++) {
            		bf.write("\t");
            		bf.write(entry.getValue().get(ix).toString());
            	}
            	bf.write("\n");
            }
  
            bf.flush();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        finally {
  
            try {
  
                // always close the writer
                bf.close();
            }
            catch (Exception e) {
            }
        }
	}
	
	private static void writeIds(Map<Id<Vehicle>,	ArrayList<Id<Link>>> outMap, String outFname) throws IOException 
	{
		// new file object
        File file = new File(outFname);
  
        BufferedWriter bf = null;
  
        try {
  
            // create new BufferedWriter for the output file
            bf = new BufferedWriter(new FileWriter(file));
  
            // iterate map entries
            for (Entry<Id<Vehicle>, ArrayList<Id<Link>>> entry :
            	outMap.entrySet()) {
 
            	bf.write(entry.getKey().toString() + ":");
            	
            	int size = entry.getValue().size();
            	if (size==0) {
            		bf.write("\n");
            	}
            	for (int ix=0; ix<size; ix++) {
            		bf.write("\t");
            		bf.write(entry.getValue().get(ix).toString());
            	}
            	bf.write("\n");
            }
  
            bf.flush();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        finally {
  
            try {
  
                // always close the writer
                bf.close();
            }
            catch (Exception e) {
            }
        }
	}
	
	
	@Override
	public void notifyIterationStarts(IterationStartsEvent	event) {
			System.out.println("Iteration " + event.getIteration() + " begins!");
			event.getServices().getEvents().addHandler(this.myEventHandler);
	}
	
	@Override
	public void notifyIterationEnds(IterationEndsEvent	event) {
		if	(event.getIteration()	%	iterAnalysis	==	0 && event.getIteration() != 0)	{
			event.getServices().getEvents().removeHandler(this.myEventHandler);
			File theDir = new File(this.outFolder);
			if (!theDir.exists()) {
				theDir.mkdirs();
			}
			String	outputRoutes			=	this.outFolder + "routes.txt";
			String	outputTravelTimes		=	this.outFolder + "travelTimes.txt";
			String	outputLinkEnterIds		=	this.outFolder + "linkEnterIds.txt";
//			String	outputLinkExitIds		=	this.outFolder + "linkExitIds.txt";
			String	outputLinkEnterTimes	=	this.outFolder + "linkEnterTimes.txt";
//			String	outputLinkExitTimes		=	this.outFolder + "linkExitTimes.txt";
			
			try {
				writeTravelTtime(this.myEventHandler.travelTimesReport(), outputTravelTimes);
				writeTimes(this.myEventHandler.linkEnterTimesReport(), outputLinkEnterTimes);
//				writeTimes(this.myEventHandler.linkExitTimesReport(), outputLinkExitTimes);
				writeIds(this.myEventHandler.linkEnterIdsReport(), outputLinkEnterIds);
//				writeIds(this.myEventHandler.linkExitIdsReport(), outputLinkExitIds);
				writeIds(this.myEventHandler.travelRoutesReport(), outputRoutes);
				
			} catch (IOException e) {
				e.printStackTrace();
			}
			
		}
	}
}
