package seattle;
import java.io.File;

import org.matsim.api.core.v01.Scenario;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigUtils;
import org.matsim.core.controler.Controler;
import org.matsim.core.scenario.ScenarioUtils;

public class runMATSim {

	public static void main(String[] args) {	    
		File currDir = new File(".");
		String path = currDir.getAbsolutePath();
		path = path.substring(0, path.length()-1);
		System.out.println(path);
		
		//=================================
		//   split scenario configuration
		//=================================
		int split = 1; //1: true; 0: false
		
		String	folder		=	path + "scenarios\\seattle-formal-all\\justAcase\\MATSim\\";
		int scenarioCnt		= 	1;
		String splitStr = "";
		
		if (split==1) {
			splitStr = ".split";
		}
		
		String	outfolder	=	folder + scenarioCnt + splitStr + ".output\\";
		String	outfolder_extra	=	folder + scenarioCnt + splitStr + ".output_extra\\";
		String	configFname	=	folder + scenarioCnt + splitStr + ".seattleConfig" + ".xml";
		Config	config		=	ConfigUtils.loadConfig(configFname);
		config.controler().setOutputDirectory(outfolder);
		config.controler().setLastIteration(50);
		
		run(folder, config, outfolder_extra);
	}
	
	static void run(String folder, Config config, String outfolder_extra) {
		Scenario scenario = ScenarioUtils.loadScenario(config);
		
		scenario = ScenarioUtils.loadScenario(config);
		
		Controler controler = new Controler(scenario);
		controler.addControlerListener(new	MyControlerListener(outfolder_extra));
		
		controler.run();
	}
}
