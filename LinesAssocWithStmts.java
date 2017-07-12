
/*import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.AssertStatement;
import org.eclipse.jdt.core.dom.Block;
import org.eclipse.jdt.core.dom.BreakStatement;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.ConstructorInvocation;
import org.eclipse.jdt.core.dom.ContinueStatement;
import org.eclipse.jdt.core.dom.DoStatement;
import org.eclipse.jdt.core.dom.EmptyStatement;
import org.eclipse.jdt.core.dom.EnhancedForStatement;
import org.eclipse.jdt.core.dom.ExpressionStatement;
import org.eclipse.jdt.core.dom.ForStatement;
import org.eclipse.jdt.core.dom.IfStatement;
import org.eclipse.jdt.core.dom.LabeledStatement;
import org.eclipse.jdt.core.dom.MethodRef;
import org.eclipse.jdt.core.dom.ReturnStatement;
import org.eclipse.jdt.core.dom.SuperConstructorInvocation;
import org.eclipse.jdt.core.dom.SwitchCase;
import org.eclipse.jdt.core.dom.SwitchStatement;
import org.eclipse.jdt.core.dom.SynchronizedStatement;
import org.eclipse.jdt.core.dom.ThrowStatement;
import org.eclipse.jdt.core.dom.TryStatement;
import org.eclipse.jdt.core.dom.TypeDeclarationStatement;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement;
import org.eclipse.jdt.core.dom.WhileStatement;
import org.eclipse.jdt.core.dom.rewrite.ASTRewrite;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.Statement;*/
import org.eclipse.jdt.core.dom.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import org.eclipse.jdt.core.JavaCore;
import java.util.Map;
import org.eclipse.jdt.core.dom.AST;
 

//Example of usage: java -cp .:libsLAWS/* LinesAssocWithStmts


public class LinesAssocWithStmts {


	public static void main(String[] args) {
		ASTVisitor visitor=new ASTVisitor() {
 
			Set names = new HashSet();
			
			public boolean visit(Statement node) {
				System.out.println("Entro a Statement");	
				//System.out.println("Declaration of '" + node + "' at line"
				//		+ cu.getLineNumber(node.getStartPosition()));
				return false; // do not continue 
			}
 
			/*public boolean visit(VariableDeclarationFragment node) {
				System.out.println("Entro a VariableDeclatoinFragment");	
				SimpleName name = node.getName();
				this.names.add(name.getIdentifier());
				//System.out.println("Declaration of '" + name + "' at line"
					//	+ cu.getLineNumber(name.getStartPosition()));
				return false; // do not continue 
			}
 
			public boolean visit(SimpleName node) {
				System.out.println("Entro a SimpleName");
				if (this.names.contains(node.getIdentifier())) {
					//System.out.println("Usage of '" + node + "' at line "
						//	+ cu.getLineNumber(node.getStartPosition()));
				}
				return true;
			}
		};
		String str=args[0];
		int parserVersion = AST.JLS8;
		
		//parserVersion = AST.JLS4;
		
		ASTParser parser = ASTParser.newParser(parserVersion);
		String[] libs= new String[0];
		parser.setEnvironment(libs, new String[] {}, null, true);
		
		Map options = JavaCore.getOptions();
		JavaCore.setComplianceOptions(JavaCore.VERSION_1_8, options);
		options.put(JavaCore.COMPILER_SOURCE, JavaCore.VERSION_1_8);
		parser.setCompilerOptions(options);
		
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
		parser.setResolveBindings(true);
		parser.setBindingsRecovery(true);
		parser.setStatementsRecovery(true);
		parser.setSource(str.toCharArray());
		
		ParserRequestor req = new ParserRequestor(visitor);
		parser.createASTs(new String[]{str}, null, new String[0], req, null);
		//CompilationUnit cu = visitor.getCompilationUnit();
		
		//CompilationUnit cu = (CompilationUnit) parser.createAST(null);
		
		
		/*
		String str=args[0];
		System.out.println("Entro al main "+ str);
		ASTParser parser = ASTParser.newParser(AST.JLS3);
		parser.setSource(str.toCharArray());
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
 		Map options = JavaCore.getOptions();
		JavaCore.setComplianceOptions(JavaCore.VERSION_1_7, options);
		parser.setCompilerOptions(options);
		final CompilationUnit cu = (CompilationUnit) parser.createAST(null);
 */
		//cu.accept();
		
		/*
	
		String docAddress = args[0];
		ASTParser parser = ASTParser.newParser(AST.JLS4);
		//parser.setEnvironment(libs, new String[] {}, null, true);
		//parser.setCompilerOptions(options);
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
		parser.setResolveBindings(true);
		parser.setBindingsRecovery(true);
		parser.setStatementsRecovery(true);
		ParserRequestor req = new ParserRequestor(visitor);
		parser.createASTs(new String[]{docAddress}, null, new String[0], req, null);
		this.compilationUnit = visitor.getCompilationUnit();
	
	
	
	
	
 
 		//ASTParser parser = ASTParser.newParser(AST.JLS3);
 		String docAddress = args[0];
		//Document doc = new Document(docAddress);
 		//parser.setSource(doc.get().toCharArray());
		
		//parser.setSource("int i = 9; \n int j = i+1;".toCharArray());
 
		//parser.setKind(ASTParser.K_STATEMENTS);
		Block block = (Block) parser.createAST(null);
 
		//here can access the first element of the returned statement list
		//String str = block.statements().get(0).toString();
		//System.out.println(str);
 
		block.accept(new ASTVisitor() {
 
			public boolean visit(ExpressionStatement node) {
 
				System.out.println("Name: " + node);
 
				return true;
			}
 
		});*/
	}
	
	
	
}

class ParserRequestor extends FileASTRequestor
	{
	private ASTVisitor visitor;
	
	public ParserRequestor(ASTVisitor v)
	{
		this.visitor = v;
	}

	@Override
	public void acceptAST(String sourceFilePath, CompilationUnit ast)
	{
		//this.visitor.setCompilationUnit(ast);
		ast.accept(this.visitor);
		super.acceptAST(sourceFilePath, ast);
	}
}







/*
int parserVersion = AST.JLS8;
		if(Configuration.sourceVersion != "1.8") {
			parserVersion = AST.JLS4;
		}
		ASTParser parser = ASTParser.newParser(parserVersion);
		parser.setEnvironment(libs, new String[] {}, null, true);
		
		Map options = JavaCore.getOptions();
		JavaCore.setComplianceOptions(Configuration.sourceVersion, options);
		if(!Configuration.sourceVersion.equals("1.8")) { // FIXME: make this less fragile
		options.put(JavaCore.COMPILER_SOURCE, JavaCore.VERSION_1_7);
		} else {
			options.put(JavaCore.COMPILER_SOURCE, JavaCore.VERSION_1_8);			
		}
		parser.setCompilerOptions(options);
		
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
		// note that this bindings recovery and resolution are important for
		// checking information about types, down the line.
		parser.setResolveBindings(true);
		parser.setBindingsRecovery(true);
		parser.setStatementsRecovery(true);
		ParserRequestor req = new ParserRequestor(visitor);
		
		parser.createASTs(new String[]{file}, null, new String[0], req, null);
		
		this.compilationUnit = visitor.getCompilationUnit();
*/
