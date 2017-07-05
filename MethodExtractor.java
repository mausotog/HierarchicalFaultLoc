//package clegoues.genprog4java.fitness;

//import static clegoues.util.ConfigurationBuilder.BOOLEAN;
//import static clegoues.util.ConfigurationBuilder.DOUBLE;
//import static clegoues.util.ConfigurationBuilder.STRING;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.PrintWriter;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

//import org.apache.commons.lang3.tuple.Pair;
//import org.apache.log4j.Logger;
import org.junit.runner.Description;
import org.junit.runner.Request;
/*
import clegoues.genprog4java.main.Configuration;
import clegoues.genprog4java.mut.Mutation;
import clegoues.genprog4java.mut.WeightedMutation;
import clegoues.genprog4java.rep.Representation;
import clegoues.util.ConfigurationBuilder;
*/
import junit.framework.Test;
import junit.framework.TestSuite;

/**
 * This class manages fitness evaluation for a variant of an arbitrary {@link clegoues.genprog4java.rep.Representation}.
 * Its duties consist of loading/tracking the test cases to be run and managing the sampling strategy, if applicable.
 * @author clegoues
 *
 */
@SuppressWarnings("rawtypes")
public class MethodExtractor {

	/** public because {@link clegoues.genprog4java.rep.CachingRepresentation} gets at them
	 * for sanity checking.  There's probably a better way to do that, I suppose, but whatever.
	 */

	public String methodsPosFileName="methods.pos"; 
	public String methodsNegFileName="methods.neg"; 

	public static ArrayList<String> positiveTests = new ArrayList<String>();
	public static ArrayList<String> negativeTests = new ArrayList<String>();

	private static int numPositiveTests;
	private static int numNegativeTests;

	String urlsTestPath;
	
	/**
	 * Loads the tests from specified files, initializes the sample vars to not be null.
	 * Samples properly when the search actually begins.
	 * Note that this <i>must</i> be called before the initial representation is
	 * constructed, otherwise the rep will not be able to test itself via sanity checking.
	 */
	public MethodExtractor(String posTestFile, String negTestFile, String urlsTestPath) {
		//WE COULD ALSO GET THIS FROM defects4j export -p cp.test I THINK
		this.urlsTestPath = urlsTestPath;

		ArrayList<String> intermedPosTests = null, intermedNegTests = null;

		methodsPosFileName=posTestFile.substring(0,posTestFile.lastIndexOf("/"))+"/methods.pos";
		methodsNegFileName=negTestFile.substring(0,negTestFile.lastIndexOf("/"))+"/methods.neg";

		intermedPosTests = getTests(posTestFile);
		intermedNegTests = getTests(negTestFile);

		explodeTestClasses(intermedPosTests, intermedNegTests);

		for(String posTest : intermedPosTests) {
			positiveTests.add(posTest);
			
		}
		writeToFile(methodsPosFileName, positiveTests);
		
		for(String negTest : intermedNegTests) {
			negativeTests.add(negTest);
		}
		writeToFile(methodsNegFileName, negativeTests);
		
	}

	private void writeToFile(String fileName, ArrayList<String> tests){
		try{
		    PrintWriter writer = new PrintWriter(fileName, "UTF-8");
		    for(String t : tests){
		    	writer.println(t);
			System.out.println("Writting to file: "+ t);
		    }
		    writer.close();
		} catch (IOException e) {
		   // do something
		}
	}

	/** As mentioned: JUnit is annoying.  If test granularity is set to "method", then,
	 * unlike the default behavior lo these many months, we actually run one method at a time.
	 * However, specifying tests one method at a time is also annoying (and not what D4J, at
	 * least, does by default for the passing tests). This method thus "explodes" the test classes
	 * into their constituent methods.
	 * 
	 * @param intermedPosTests
	 * @param intermedNegTests
	 * @throws MalformedURLException 
	 * @throws ClassNotFoundException 
	 */

	private URLClassLoader testLoader() throws MalformedURLException {
		String urlsTestPath="/home/mau/Research/defects4jJava8/defects4j/ExamplesCheckedOut/math2Buggy/target/classes:/home/mau/Research/defects4jJava8/defects4j/ExamplesCheckedOut/math2Buggy/target/test-classes:/home/mau/Research/MLFaultLocProject/GPLibs/junit-4.12.jar:/home/mau/Research/defects4jJava8/defects4j/ExamplesCheckedOut/math2Buggy/lib/junit-4.8.2.jar";
		String[] split = urlsTestPath.split(":");
		URL[] urls = new URL[split.length];
		for(int i = 0; i < split.length; i++) {
			String s = split[i];
			File f = new File(s);
			URL url = f.toURI().toURL();
			urls[i] = url;
		}
		for(int i=0; i<urls.length;++i)
			System.out.println("url: "+urls[i]);
		return new URLClassLoader(urls);
	}
	
	private static boolean looksLikeATest(Method m) {
		return (m.isAnnotationPresent(org.junit.Test.class) ||
				(m.getParameterTypes().length == 0 &&
				m.getReturnType().equals(Void.TYPE) &&
				Modifier.isPublic(m.getModifiers()) &&
				m.getName().startsWith("test")));
	}
    
	private ArrayList<String> getTestMethodsFromClazz(String clazzName, URLClassLoader testLoader) {
		System.out.println("");
		System.out.println("clazzName: " + clazzName + " testLoader: "+ testLoader.getURLs()[0] );
		ArrayList<String> realTests = new ArrayList<String>();
		try {
			clazzName=clazzName.replace("/",".");
			//String[] arr = clazzName.split("/");
			//clazzName=arr[arr.length-1];			
			if(clazzName.endsWith("/java")) clazzName=clazzName.substring(0,clazzName.length()-5);
			//System.out.println(clazzName);
			Class<?> testClazz = Class.forName(clazzName, true, testLoader);
		    try {
System.out.println(testClazz);
				TestSuite actualTest = (TestSuite) testClazz.getMethod("suite").invoke(testClazz);

		System.out.println("here");
				int numTests = actualTest.countTestCases();
				for(int i = 0; i < numTests; i++) {
					Test t = actualTest.testAt(i);
					String testName = t.toString();
					String[] split = testName.split(Pattern.quote("("));
					String methodName = split[0];
					realTests.add(methodName);
				}
		    } catch (NoSuchMethodException |IllegalAccessException | IllegalArgumentException | InvocationTargetException | SecurityException e) {
			// invoke of "suite" likely failed.  Try something else.
			  // Given a bunch of classes, find all of the JUnit test-methods defined by them.
		      for (Description test : Request.aClass(testClazz).getRunner().getDescription().getChildren()) {
		        // a parameterized atomic test case does not have a method name
		        if (test.getMethodName() == null) {
		          for (Method m : testClazz.getMethods()) {
		            // JUnit 3: an atomic test case is "public", does not return anything ("void"), has 0
		            // parameters and starts with the word "test"
		            // JUnit 4: an atomic test case is annotated with @Test
		            if (looksLikeATest(m)) {
		              realTests.add(m.getName()); // test.getDisplayName()
		            }
		          }
		        } else {
		          // non-parameterized atomic test case
		          realTests.add(test.getMethodName());
		        }
		      }
		    }
		} catch (ClassNotFoundException e) {
			
			System.out.println("Test class " + clazzName + " not found in ExplodeTests!");
			System.out.println("");
		}
		return realTests;
	}
	
	private void explodeTestClasses(ArrayList<String> initialPosTests, ArrayList<String> initialNegTests) {
		ArrayList<String> realPosTests = new ArrayList<String>();
		try {
			URLClassLoader testLoader = testLoader();
			// First, get the negative classes.  
			// need to do this to filter the positive classes, since
			// we can't actually call filterTestClasses first
			HashMap<String, List<String>> negClazzes = new HashMap<String, List<String>>(); 
			// get all classes containing failing tests, as well as those failing tests
			for(String testName : initialNegTests) {
				if(testName.contains("::")) {
					String[] split = testName.split("::");
					String clazzName = split[0];
					String methodName = split[1].trim();
					List<String> methodList;
					if(negClazzes.containsKey(clazzName)) {
						methodList = negClazzes.get(clazzName);
					} else {
						methodList = new ArrayList<String>();
						negClazzes.put(clazzName,methodList);
					}
					methodList.add(methodName);
				}
			}
			
			
			for(String clazzName : negClazzes.keySet()) {
				if(initialPosTests.contains(clazzName)) {
					initialPosTests.remove(clazzName);
				}
			}
		
			// deal with the simple case: get all public methods from the 
			// initially positive classes and I'm 90% sure this isn't going to work
			for(String clazzName : initialPosTests) {
				if(!clazzName.contains("::")) {
					System.out.println("got here");
					for(String m : getTestMethodsFromClazz(clazzName, testLoader)) {
						realPosTests.add(clazzName + "::" + m);
					}
				} else {
					realPosTests.add(clazzName);
				}
			}
			
			for(Map.Entry<String, List<String>> entry : negClazzes.entrySet()) {
				String clazzName = entry.getKey();
				List<String> negMethods = entry.getValue();
				for(String m : getTestMethodsFromClazz(clazzName, testLoader)) {
					if(!negMethods.contains(m)) {
						realPosTests.add(clazzName + "::" + m);
					}
				}
			}
			
			initialPosTests.clear();
			initialPosTests.addAll(realPosTests);
		} catch (MalformedURLException e) {
			System.out.println("malformedURLException, giving up in a profoundly ungraceful way.");
			Runtime.getRuntime().exit(1);
		}
	}
	
	/** load tests from a file.  Does not check that the tests are valid, just that the file exists.
	 * If the file doesn't exist, kills the runtime to exit, because that means that things have gone VERY
	 * weird.
	 * @param filename file listing test classes or test class::methods, one per line.
	 */
	private ArrayList<String> getTests(String filename) {
		ArrayList<String> allLines = new ArrayList<String>();
		try {
			BufferedReader br = new BufferedReader(new FileReader(filename));
			String line;
			allLines = new ArrayList<String>();
			while ((line = br.readLine()) != null) {
				allLines.add(line);
			}
			br.close();
		} catch(IOException e) {
			System.out.println("failed to read " + filename + " giving up");
			Runtime.getRuntime().exit(1);
		}
		return allLines;
	}

	public static void main(String[] args){
		MethodExtractor me = new MethodExtractor(args[0],args[1],args[2]);
		
	}

	

}
