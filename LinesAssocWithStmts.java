
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
 
			public boolean visit(VariableDeclarationFragment node) {
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


