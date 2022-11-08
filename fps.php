<?php

$dir = new DirectoryIterator(dirname(__FILE__));

foreach($dir as $fileInfo){
	
	if(!$fileInfo-> isDot()){
		
		$stringName = strval($fileInfo-> getFilename());

		if(strpos($stringName, "mp4") !== false && $stringName === 'output.mp4'){
			
			
			exec('ffmpeg -i "' . $stringName . '" -filter:v fps=fps=30 "'.str_replace("_final", "", $stringName));
		}else if(strpos($stringName, "output") !== false && 
				(strpos($stringName, "mp4") !== false || 
				 strpos($stringName, "mp3") !== false || 
				 strpos($stringName, "wav") !== false ||
				 strpos($stringName, "mkv") !== false || 
				 strpos($stringName, "avi") !== false)){

			unlink($stringName);
		}else if(strpos($stringName, "jpg") !== false || strpos($stringName, "txt") !== false){

			unlink($stringName);
		}		
	}
}
