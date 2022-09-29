import pandas as pd
import aspose.words as aw
import streamlit as st
import pickle
import os
from streamlit_tags import st_tags
from pyresparser import ResumeParser
import nltk
nltk.download()
    
# def image(image_file):
#     l = []
#     img = cv2.imread(image_file)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
#     rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
#     dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
#     contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
#     cv2.CHAIN_APPROX_NONE)
#     im2 = img.copy()
#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)
#         rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         cropped = im2[y:y + h, x:x + w]
#         text = pytesseract.image_to_string(cropped)
#         l.append(text)
#         wor = ['%','\n']
#         for word in wor:
#             for i in range(len(l)):
#                 if word in l[i]:
#                     l[i] = l[i].replace(word,'')
#     return l

      
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
    st.success("** This Resume is suitable for {} Jobs **".format(le.inverse_transform(predicted)[0]))


def save_uploadedfile(uploadedfile):
    
    with open(os.path.join(r"C:\Users\AyushKumar.Gupta\Downloads",uploadedfile.name),"wb") as f:
        x = os.path.join(r"C:\Users\AyushKumar.Gupta\Downloads",uploadedfile.name)
        f.write(uploadedfile.getbuffer())
    return x

def data_1(x):
    resume_data = ResumeParser(x).get_extracted_data()  
    resume_data_1 = resume_data['skills']
    for i in range(len(resume_data_1)):
        resume_data_1[i] = resume_data_1[i].lower()
        
    return resume_data_1
    

def data(x,key_):
    
    resume_data = ResumeParser(x).get_extracted_data()  
    resume_data_1 = resume_data['skills']
    for i in range(len(resume_data_1)):
        resume_data_1[i] = resume_data_1[i].lower()
    if resume_data:
    ## Get the whole resume data

        st.header("**Resume Analysis**")
        st.success("Hello "+ resume_data['name'])
        st.subheader("**Your Basic info**")
        try:
            st.text('Name: '+resume_data['name'])
            st.text('Email: ' + resume_data['email'])
            st.text('Contact: ' + resume_data['mobile_number'])
            st.text('Resume pages: '+str(resume_data['no_of_pages']))
        except:
            pass

    keywords = st_tags(label='### Skills that you have',
            value=resume_data['skills'],key = key_)   
            
    reco_field = prediction(resume_data_1)
    return resume_data_1
    
    

def main():
    c=0
    st.title("Resume Classifier")
    menu = ["Resume_classification","Job_Match","About"]
    choice = st.sidebar.selectbox("Menu",menu)
    
    if choice=="Resume_classification":
        st.subheader("Files")
        uploaded_files = st.file_uploader("Upload your resume", type=["pdf","docx","doc"],accept_multiple_files=True)
        for uploaded_file in uploaded_files:
            x = save_uploadedfile(uploaded_file)
            if x.split('.')[-1] == 'doc':
                doc = aw.Document(x)
                x = os.path.join(r"C:\Users\AyushKumar.Gupta\Downloads",uploaded_file.name+'.pdf')
                doc.save(x)
                data(x,str(c))
                
            else:
                data(x,str(c))
                
    elif choice == 'Job_Match':
        st.subheader("Files")
        uploaded_files = st.file_uploader("Upload candidate resume", type=["pdf","docx","doc"],accept_multiple_files=True)
        job_files = st.file_uploader("Choose job description file", type=["pdf"],accept_multiple_files=True)
        for job_file in job_files:
            x = save_uploadedfile(job_file)
            k = data_1(x)
            for uploaded_file in uploaded_files:
                c=c+1
                x = save_uploadedfile(uploaded_file)
                if x.split('.')[-1] == 'doc':
                    doc = aw.Document(x)
                    x = os.path.join(r"C:\Users\AyushKumar.Gupta\Downloads",uploaded_file.name+'.pdf')
                    doc.save(x)
                    s = data(x,str(c))
                    count = 0
                    for i in k:
                        if i in s:
                            count +=1

                    sim_score = count/len(k)
                    sim_score = sim_score * 100
                    st.success("Job Fittment: "+ str(sim_score)) 

                else: 
                    s = data(x,str(c))
                    count = 0
                    for i in k:
                        if i in s:
                            count +=1

                    sim_score = count/len(k)
                    sim_score = sim_score * 100
                    st.success("Job Fittment: "+ str(sim_score))          
            

    else:
        st.subheader("About")
        st.text("Built with streamlit and Python")

if __name__=='__main__':
    main()
