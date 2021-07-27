package seattle;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.events.ActivityEndEvent;
import org.matsim.api.core.v01.events.ActivityStartEvent;
import org.matsim.api.core.v01.events.LinkEnterEvent;
import org.matsim.api.core.v01.events.LinkLeaveEvent;
import org.matsim.api.core.v01.events.PersonArrivalEvent;
import org.matsim.api.core.v01.events.PersonDepartureEvent;
import org.matsim.api.core.v01.events.handler.ActivityEndEventHandler;
import org.matsim.api.core.v01.events.handler.ActivityStartEventHandler;
import org.matsim.api.core.v01.events.handler.LinkEnterEventHandler;
import org.matsim.api.core.v01.events.handler.LinkLeaveEventHandler;
import org.matsim.api.core.v01.events.handler.PersonArrivalEventHandler;
import org.matsim.api.core.v01.events.handler.PersonDepartureEventHandler;
import org.matsim.api.core.v01.network.Link;
import org.matsim.api.core.v01.population.Person;
import org.matsim.vehicles.Vehicle;

public class MyEventHandler implements PersonDepartureEventHandler, PersonArrivalEventHandler
, LinkEnterEventHandler, LinkLeaveEventHandler, ActivityStartEventHandler, ActivityEndEventHandler{
	private	Map<Id<Person>,		ArrayList<Double>>	travelTimes			=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Id<Link>>>	travelRoutes	=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Id<Link>>>	linkEnterIds	=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Id<Link>>>	linkExitIds		=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Double>>	linkEnterTimes		=	new	HashMap<>();
	private	Map<Id<Vehicle>,	ArrayList<Double>>	linkExitTimes		=	new	HashMap<>();
	public Map<Id<Vehicle>,		Integer>			activityCnts		=	new HashMap<>();

	public MyEventHandler(Map<Id<Person>, ArrayList<Double>> travelTimes, Map<Id<Vehicle>,	
			ArrayList<Id<Link>>> travelRoutes, Map<Id<Vehicle>,	ArrayList<Id<Link>>> linkEnterIds,
			Map<Id<Vehicle>, ArrayList<Id<Link>>> linkExitIds, Map<Id<Vehicle>,	ArrayList<Double>> linkEnterTimes,
			Map<Id<Vehicle>, ArrayList<Double>>	linkExitTimes, Map<Id<Vehicle>,	Integer> activityCnts) {
		
		this.travelTimes = travelTimes;
		this.travelRoutes = travelRoutes;
		this.linkEnterIds = linkEnterIds;
		this.linkExitIds = linkExitIds;
		this.linkEnterTimes = linkEnterTimes;
		this.linkExitTimes = linkExitTimes;
		this.activityCnts = activityCnts;
	}
	
	@Override
	public void handleEvent(PersonDepartureEvent	event) {
			Id<Person> personID = event.getPersonId();
			
			// based on the activity, we determine new personID
			if (this.activityCnts.size() > 0) {
				personID = Id.createPersonId(personID + "_" + this.activityCnts.get(personID).toString());
			} else {
				personID = Id.createPersonId(personID + "_1");
			}
			
			
			ArrayList<Double> times = new ArrayList<Double>();
			times.add(event.getTime());
			this.travelTimes.put(personID, times);
			
			// enter and exit times are the same when departure
			ArrayList<Id<Link>> route = new ArrayList<Id<Link>>();
			ArrayList<Double> linkEnterTime = new ArrayList<Double>();
			ArrayList<Id<Link>> linkEnterId = new ArrayList<Id<Link>>();
			route.add(event.getLinkId());
			linkEnterTime.add(event.getTime());
			linkEnterId.add(event.getLinkId());
			this.travelRoutes.put(Id.createVehicleId(personID), route);
			this.linkEnterTimes.put(Id.createVehicleId(personID), linkEnterTime);
			this.linkEnterIds.put(Id.createVehicleId(personID), linkEnterId);
	}
	
	@Override
	public void handleEvent(ActivityStartEvent event) {
		String eventType = event.getActType();
		Id<Person> personID = event.getPersonId();
		
		if (eventType=="home") {
			this.activityCnts.put(Id.createVehicleId(personID), 1);
		} else if (eventType=="work") {
			this.activityCnts.put(Id.createVehicleId(personID), 2);
		}
		//odds: home->work; evens: work->home
	}
	
	@Override
	public void handleEvent(ActivityEndEvent event) {
		String eventType = event.getActType();
		Id<Person> personID = event.getPersonId();
		
		if (eventType=="home") {
			this.activityCnts.put(Id.createVehicleId(personID), 1);
		} else if (eventType=="work") {
			this.activityCnts.put(Id.createVehicleId(personID), 2);
		}
		//odds: home->work; evens: work->home
	}
	
	@Override
	public void handleEvent(PersonArrivalEvent	event) {
		Id<Person> personID		=	event.getPersonId();
		
		// based on the activity, we determine new personID
		if (this.activityCnts.size() > 0) {
			personID = Id.createPersonId(personID + "_" + this.activityCnts.get(personID).toString());
		} else {
			personID = Id.createPersonId(personID + "_1");
		}
		
					
		double	departureTime	=	this.travelTimes.get(personID).get(0); // departure time, arrival time, travel time
		double	travelTime		=	event.getTime()	- departureTime;
		ArrayList<Double> times = new ArrayList<Double>();
		times.add(departureTime);
		times.add(event.getTime());
		times.add(travelTime);
		this.travelTimes.put(personID, times);
		
		// output exit times when arrival
		ArrayList<Id<Link>> linkExitId = new ArrayList<Id<Link>>();
		ArrayList<Double> linkExitTime = new ArrayList<Double>();
		linkExitTime.add(event.getTime());
		linkExitId.add(event.getLinkId());
	}
	
	@Override
	public void handleEvent(LinkEnterEvent event) {
		Id<Vehicle> personID	=	event.getVehicleId();
		
		// based on the activity, we determine new personID
		if (this.activityCnts.size() > 0) {
			personID = Id.createVehicleId(personID + "_" + this.activityCnts.get(personID).toString());
		} else {
			personID = Id.createVehicleId(personID + "_1");
		}
		
		ArrayList<Id<Link>> route = new ArrayList<Id<Link>>();
		ArrayList<Double> linkEnterTime = new ArrayList<Double>();
		ArrayList<Id<Link>> linkEnterId = new ArrayList<Id<Link>>();
		
		if (this.travelRoutes.containsKey(personID)) {
			route = this.travelRoutes.get(personID);
		}
		
		if (this.linkEnterTimes.containsKey(personID)) {
			linkEnterTime = this.linkEnterTimes.get(personID);
		}
		
		if (this.linkEnterIds.containsKey(personID)) {
			linkEnterId = this.linkEnterIds.get(personID);
		}
		
		if (route.size()==0) {
			route.add(event.getLinkId());
			linkEnterTime.add(event.getTime());
			linkEnterId.add(event.getLinkId());
			this.travelRoutes.put(personID, route);
			this.linkEnterTimes.put(personID, linkEnterTime);
			this.linkEnterIds.put(personID, linkEnterId);
		} else {
			if (route.get(route.size()-1)!=event.getLinkId()) {
				route.add(event.getLinkId());
				linkEnterTime.add(event.getTime());
				linkEnterId.add(event.getLinkId());
				this.travelRoutes.put(personID, route);
				this.linkEnterTimes.put(personID, linkEnterTime);
				this.linkEnterIds.put(personID, linkEnterId);
			}
		}
	}
	
	@Override
	public void handleEvent(LinkLeaveEvent event) {
		Id<Vehicle> personID	=	event.getVehicleId();
		
		// based on the activity, we determine new personID
		if (this.activityCnts.size() > 0) {
			personID = Id.createVehicleId(personID + "_" + this.activityCnts.get(personID).toString());
		} else {
			personID = Id.createVehicleId(personID + "_1");
		}
		
		ArrayList<Id<Link>> linkExitId = new ArrayList<Id<Link>>();
		ArrayList<Double> linkExitTime = new ArrayList<Double>();
		
		if (this.linkExitIds.containsKey(personID)) {
			linkExitId = this.linkExitIds.get(personID);
		}
		
		if (this.linkExitTimes.containsKey(personID)) {
			linkExitTime = this.linkExitTimes.get(personID);
		}
		
		if (linkExitId.size()==0) {
			linkExitId.add(event.getLinkId());
			linkExitTime.add(event.getTime());
			this.linkExitIds.put(personID, linkExitId);
			this.linkExitTimes.put(personID, linkExitTime);
		}else {
			if (linkExitId.get(linkExitId.size()-1)!=event.getLinkId()) {
				linkExitId.add(event.getLinkId());
				linkExitTime.add(event.getTime());
				this.linkExitIds.put(personID, linkExitId);
				this.linkExitTimes.put(personID, linkExitTime);
			}
		}
	}
	
	public Map<Id<Person>, ArrayList<Double>> travelTimesReport(){
		return this.travelTimes;
	}
	
	public Map<Id<Vehicle>,	
	ArrayList<Id<Link>>> travelRoutesReport(){
		return this.travelRoutes;
	}
	
	public Map<Id<Vehicle>,	ArrayList<Id<Link>>> linkEnterIdsReport(){
		return this.linkEnterIds;
	}
	
	public Map<Id<Vehicle>, ArrayList<Id<Link>>> linkExitIdsReport(){
		return this.linkExitIds;
	}
	
	public Map<Id<Vehicle>,	ArrayList<Double>> linkEnterTimesReport(){
		return this.linkEnterTimes;
	}
	
	public Map<Id<Vehicle>,	ArrayList<Double>> linkExitTimesReport(){
		return this.linkExitTimes;
	}
}
