import nltk
#nltk.download('stopwords', download_dir='/usr/local/share/nltk_data')
#nltk.data.path.append('/usr/local/share/nltk_data')
!python -m nltk.downloader stopwords
import os
import pickle
import aspose.words as aw
from flask_cors import CORS
from pyresparser import ResumeParser
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
CORS(app)

        
def remove_brackets(data):
    data = data.replace('[','')
    data = data.replace(']','')
    data = data.replace(',',' ')
    data = data.replace('\'','')
    #print(data)
    return data

def prediction(skills_data):
    skills_data = str(skills_data)
    skills = remove_brackets(skills_data)
    with open('clf_model_pkl' , 'rb') as f:
        clf = pickle.load(f)
    with open('vectorizer_pkl' , 'rb') as f:
        vec = pickle.load(f)
    with open('le_pkl' , 'rb') as f:
        le = pickle.load(f)
    feature = vec.transform([skills])
    predicted = clf.predict(feature)
    return (le.inverse_transform(predicted)[0])

def data_extraction_jd(x):
    jd_data = ResumeParser(x).get_extracted_data()  
    jd_data_skills = jd_data['skills']
    for i in range(len(jd_data_skills)):
        jd_data_skills[i] = jd_data_skills[i].lower()    
    return jd_data_skills
    

def data_extraction_resume(x):
    val = {} 
    resume_data = ResumeParser(x).get_extracted_data() 
    resume_data_skills = resume_data['skills']
    for i in range(len(resume_data_skills)):
        resume_data_skills[i] = resume_data_skills[i].lower()
    if resume_data:
        desgination = prediction(resume_data_skills)
        try:
            val = {
            'name':resume_data['name'],
            'email':resume_data['email'],
            'contact': resume_data['mobile_number'],
            'resume pages':str(resume_data['no_of_pages']),
            'skills':resume_data['skills'],
            'desgination predicted':desgination
            }
        except:
            pass
    return val
       
@app.route("/predict", methods = ['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        file.save(secure_filename(file.filename))
        temp = str(file.filename)
        file_name = os.path.join(temp.replace(" ","_"))
        if file_name.split('.')[-1] == 'doc':
            doc = aw.Document(file_name)
            file_name = os.path.join(r"C:\Users",file.filename+'.pdf')
            doc.save(file_name)
            out_ = data_extraction_resume(file_name)
        else:
            out_ = data_extraction_resume(file_name)  
        return (jsonify(out_))
    

@app.route("/match", methods = ['POST'])
def match():
    if request.method == 'POST':
        resumefile = request.files['file_resume']
        descriptionfile = request.files['file_description']
        
        resumefile.save(secure_filename(resumefile.filename))
        temp = str(resumefile.filename)
        resume_file = os.path.join(temp.replace(" ","_"))
        
        descriptionfile.save(secure_filename(descriptionfile.filename))
        temp = str(descriptionfile.filename)
        description_file = os.path.join(temp.replace(" ","_"))
        jd_skill_set = data_extraction_jd(description_file)
        
        if resume_file.split('.')[-1] == 'doc':
            doc = aw.Document(resume_file)
            resume_file = os.path.join(r"C:\Users",resumefile.filename+'.pdf')
            doc.save(resume_file)
            basic_data = data_extraction_resume(resume_file)
            candidate_skills_set = data_extraction_resume(resume_file)['skills']
            count = 0
            for i in jd_skill_set:
                if i in candidate_skills_set:
                    count +=1

            sim_score = count/len(jd_skill_set)
            sim_score = sim_score * 100
            basic_data['job fittment'] = str(sim_score)
            return (jsonify(basic_data))
        else:
            basic_data = data_extraction_resume(resume_file)
            candidate_skills_set = data_extraction_resume(resume_file)['skills']
            count = 0
            for i in jd_skill_set:
                if i in candidate_skills_set:
                    count +=1

            sim_score = count/len(jd_skill_set)
            sim_score = sim_score * 100
            basic_data['job fittment'] = str(sim_score)
            return (jsonify(basic_data))      
 
if __name__ == '__main__':
    app.run(debug = True)    
