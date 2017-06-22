//package clegoues.genprog4java.fitness;

import static clegoues.util.ConfigurationBuilder.BOOLEAN;
import static clegoues.util.ConfigurationBuilder.DOUBLE;
import static clegoues.util.ConfigurationBuilder.STRING;

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

import org.apache.commons.lang3.tuple.Pair;
import org.apache.log4j.Logger;
import org.junit.runner.Description;
import org.junit.runner.Request;

import clegoues.genprog4java.main.Configuration;
import clegoues.genprog4java.mut.Mutation;
import clegoues.genprog4java.mut.WeightedMutation;
import clegoues.genprog4java.rep.Representation;
import clegoues.util.ConfigurationBuilder;
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
	
	/**
	 * Loads the tests from specified files, initializes the sample vars to not be null.
	 * Samples properly when the search actually begins.
	 * Note that this <i>must</i> be called before the initial representation is
	 * constructed, otherwise the rep will not be able to test itself via sanity checking.
	 */
	public MethodExtractor() {
		ArrayList<String> intermedPosTests = null, intermedNegTests = null;

		intermedPosTests = getTests(posTestFile);
		intermedNegTests = getTests(negTestFile);

		switch(Fitness.granularity) {
		case METHOD:
			explodeTestClasses(intermedPosTests, intermedNegTests);
		break;
		case CLASS:
		default:
			filterTestClasses(intermedPosTests, intermedNegTests);
			filterTestClasses(intermedNegTests, intermedPosTests);
			break;
		}

		for(String posTest : intermedPosTests) {
			positiveTests.add(new TestCase(TestCase.TestType.POSITIVE, posTest));
		}

		for(String negTest : intermedNegTests) {
			negativeTests.add(new TestCase(TestCase.TestType.NEGATIVE, negTest));
		}
	}


	/**
	 * JUnit is annoying.  Basically, a junit test within a larger test class can be failing.
	 * This method figures out if that's the way these tests are specified and, if so
	 * determines their class and then filters those classes out of the
	 * this method filters those classes out of the positive tests and adds them to the negative test list.
	 * Note that CLG considered just filtering out the individual methods and allowing the junittestrunner to run
	 * classes by method in addition to just by class.
	 * I didn't do it because the max test count is presently still the number of
	 * test classes specified in the test files and so we'd either need to actually count
	 * how many tests are being run in total or have the counts/weights be skewed by the one
	 * class file where we call the methods one at a time.
	 * @param toFilter list to filter
	 * @param filterBy stuff to filter out of toFilter
	 */
	private void filterTestClasses(ArrayList<String> toFilter, ArrayList<String> filterBy) {
		ArrayList<String> clazzesInFilterSet = new ArrayList<String>();
		ArrayList<String> removeFromFilterSet = new ArrayList<String>();

		// stuff in negative tests, must remove class from positive test list and add non-negative tests to list
		for(String specifiedMethod : filterBy) {
			if(specifiedMethod.contains("::")) {
				// remove from toFilter all tests that have this class name
				// remove from filterBy this particular entry and replace it with just the className
				String[] split = specifiedMethod.split("::");
				clazzesInFilterSet.add(split[0]);
				removeFromFilterSet.add(specifiedMethod);
			}
		}
		for(String removeFromFilterBy : removeFromFilterSet ) {
			filterBy.remove(removeFromFilterBy);
		}
		filterBy.addAll(clazzesInFilterSet);

		ArrayList<String> removeFromFilteredSet = new ArrayList<String>();
		for(String testNameInToFilter : toFilter ) {
			String clazzName = "";
			if(testNameInToFilter.contains("::")) {
				String[] split = testNameInToFilter.split("::");
				clazzName = split[0];
			} else {
				clazzName = testNameInToFilter;
			}
			if(clazzesInFilterSet.contains(clazzName)) {
				removeFromFilteredSet.add(testNameInToFilter);
			}
		}
		for(String removeFromFiltered : removeFromFilteredSet) {
			toFilter.remove(removeFromFiltered);
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
		String[] split = Configuration.testClassPath.split(":");
		URL[] urls = new URL[split.length];
		for(int i = 0; i < split.length; i++) {
			String s = split[i];
			File f = new File(s);
			URL url = f.toURI().toURL();
			urls[i] = url;
		}
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
		ArrayList<String> realTests = new ArrayList<String>();
		try {
		Class<?> testClazz = Class.forName(clazzName, true, testLoader);
		try {
		TestSuite actualTest = (TestSuite) testClazz.getMethod("suite").invoke(testClazz);
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
			logger.error("Test class " + clazzName + " not found in ExplodeTests!");
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
			logger.error("malformedURLException, giving up in a profoundly ungraceful way.");
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
			logger.error("failed to read " + filename + " giving up");
			Runtime.getRuntime().exit(1);
		}
		return allLines;
	}



	

}
