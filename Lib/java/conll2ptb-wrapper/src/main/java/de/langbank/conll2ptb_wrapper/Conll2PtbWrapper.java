package de.langbank.conll2ptb_wrapper;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

import edu.berkeley.nlp.PCFGLA.Binarization;
import edu.berkeley.nlp.PCFGLA.CoarseToFineMaxRuleParser;
import edu.berkeley.nlp.PCFGLA.Grammar;
import edu.berkeley.nlp.PCFGLA.Lexicon;
import edu.berkeley.nlp.PCFGLA.ParserData;
import edu.berkeley.nlp.PCFGLA.TreeAnnotations;
import edu.berkeley.nlp.syntax.Tree;
import edu.berkeley.nlp.util.Numberer;

public class Conll2PtbWrapper {

	// Class variables
	private static final String LS = System.getProperty("line.separator");
	private static final String UNKNOWN_POS = "XY";
	private static final String ENCODING = "UTF-8";
	private static final int MAX_LENGTH = 1000;
	//private static final String BERKELEY_EDGE_MODEL = "./rsrc/ger_sm5_gf.gr";
	private static final int TOK_IDX = 1;
	private static final int TAG_IDX = 3;

	// Instance variables
	private CoarseToFineMaxRuleParser parser;

	public Conll2PtbWrapper(String model) throws IOException, ClassNotFoundException {
		System.out.println("Conll2PtbWrapper: parseFilesRec: Started to load grammar from file: " + model);
		ParserData pData = ParserData.Load(model); // not with jar
		//		GZIPInputStream gzis = new GZIPInputStream(getClass().getResourceAsStream((BERKELEY_EDGE_MODEL))); // Compressed
		//		ObjectInputStream in = new ObjectInputStream(gzis); // Load objects
		//		ParserData pData = (ParserData) in.readObject(); // Read the mix of grammars
		//		in.close(); // And close the stream.
		//		gzis.close();

		if (pData == null) {
			System.out.println("Conll2PtbWrapper: parseFilesRec: Failed to load grammar from file"+ model + ".");
			System.exit(1);
		}
		Numberer.setNumberers(pData.getNumbs());
		initialize(pData.getGrammar(), pData.getLexicon(), pData.getBinarization(), 1.0, -1, false, false, false, false, false, true, true);
	}

	private void initialize(Grammar gr, Lexicon lex, Binarization bin, double unaryPenalty, int endL, boolean viterbi, boolean sub, 
			boolean score, boolean accurate, boolean variational, boolean useGoldPOS, boolean initializeCascade) {;
			parser = new CoarseToFineMaxRuleParser(gr, lex, unaryPenalty, endL, viterbi, sub, score, accurate, variational, useGoldPOS, initializeCascade);
			parser.binarization = bin;
	}

	private String createDummyTree(List<String> sentence, List<String> posTags) {
		return createDummyTree(sentence, posTags, "unknown error occurred.");
	}

	private String createDummyTree(List<String> sentence, List<String> posTags, String errorMessage) {
		StringBuilder sb = new StringBuilder();
		sb.append("(ROOT");
		for (int i = 0; i < sentence.size(); i++) {
			String token = sentence.get(i);
			// Get POS token if available, else use UNKNOWN_POS
			String pos = UNKNOWN_POS;
			if (posTags.size() < i)
				pos = posTags.get(i);
			sb.append(" (");
			sb.append(pos);
			sb.append(" ");
			sb.append(token);
			sb.append(")");
		}
		sb.append(")");
		sb.append(LS);
		System.err.println("Cannot generate proper parse. Create dummy instead. Reason: "+errorMessage);
		return sb.toString();
	}

	public void parseFile(String inFile) throws IOException {
		BufferedReader instr = new BufferedReader(new InputStreamReader(new FileInputStream(inFile), ENCODING));
		String line;
		StringBuilder sb = new StringBuilder();
		while((line = instr.readLine()) != null) {
			line = line.trim();
			// Read a full sentence from the input file
			List<String> sentence = new ArrayList<String>();
			List<String> posTags = new ArrayList<String>();
			List<String> tmp = Arrays.asList(line.split("\t"));
			if (tmp.size() == 0) 
				continue;
			sentence.add(tmp.get(TOK_IDX));
			String[] tags = tmp.get(TAG_IDX).split("-");
			posTags.add(tags[0]);
			while (!(line = instr.readLine()).equals("")) {
				tmp = Arrays.asList(line.split("\t"));
				if (tmp.size() == 0)
					break;
				sentence.add(tmp.get(TOK_IDX));
				tags = tmp.get(TAG_IDX).split("-");
				posTags.add(tags[0]);
			}
			// Parse the sentence
			if (sentence.size() > MAX_LENGTH) {
				sb.append(createDummyTree(sentence, posTags, "Sentence exceeds sentence limit."));
				continue;
			}
			Tree<String> parsedTree = parser.getBestConstrainedParse(sentence, posTags, null);
			// if it cannot be parsed, parse by yourself
			if (parsedTree.getChildren().isEmpty()) { 
				parsedTree = parser.getBestConstrainedParse(sentence, null, null);
			}
			parsedTree = TreeAnnotations.unAnnotateTree(parsedTree, true);
			if(parsedTree == null || parsedTree.toString().equalsIgnoreCase("root")) 
				sb.append(createDummyTree(sentence, posTags));
			else
				sb.append(parsedTree.toString()+LS);
		}
		instr.close();

		// Write the parse to the output file
		String outFile = inFile.substring(0, inFile.lastIndexOf('.')) + ".ptb";
		PrintWriter outstr = new PrintWriter(new OutputStreamWriter(new FileOutputStream(outFile), ENCODING));
		outstr.write(sb.toString());
		outstr.close();
	}

	public void parseFilesRec(File root) throws IOException {
		Queue<File> q = new LinkedList<File>();
		q.add(root);
		int counter = 0;
		do {
			File f = q.remove();
			//System.out.println("Conll2PtbWrapper: parseFilesRec: Evaluate file: " + f);
			if (f.isDirectory() && !f.isHidden()) {
				File[] children = f.listFiles();
				for (int j=0; j < children.length; j++ ) {
					q.add(children[j]);
				}
			} else {
				if (!f.isHidden() && f.getName().endsWith(".conll") ) {
					System.out.println("Conll2PtbWrapper: parseFilesRec: Currently processed file: " + f);
					parseFile(f.toString());
					++counter;
				} else {
					System.out.println("Conll2PtbWrapper: parseFilesRec: Skip file: " + f);
				}
			}
		} while(!q.isEmpty()); 
		System.out.println(counter + " files processed");
	}

	public static void main(String[] args) {
		if (args.length < 2) {
			System.err.println("Wrong number or arguments. Call\n> java -jar Conll2PtbWrapper.jar inputDir model_file");
			System.exit(0);
		}
		File inDir = new File(args[0]);
		try {
			Conll2PtbWrapper wrapper = new Conll2PtbWrapper(args[1]);
			wrapper.parseFilesRec(inDir);
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ClassNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}

