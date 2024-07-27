def generate_latex(data):
    # Извлечение данных из JSON
    contact = data.get('contact', {})
    education_list = data.get('education', [])
    experience_list = data.get('experience', [])
    projects_list = data.get('projects', [])
    skills_list = data.get('skills', [])
    is_english = data.get('isEnglish', True)

    # Define section titles based on the language
    section_titles = {
        "technical_skills": "Technical Skills" if is_english else "Технические навыки",
        "education": "Education" if is_english else "Образование",
        "experience": "Experience" if is_english else "Опыт работы",
        "projects": "Projects" if is_english else "Проекты"
    }

    # Ensure that contact details are not missing
    contact_name = contact.get('name', '')
    contact_phone = contact.get('phone', '')
    contact_email = contact.get('email', '')
    contact_github = contact.get('github', '')

    latex_content = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[utf8]{inputenc}
\usepackage{tabularx}
\input{glyphtounicode}
\usepackage[utf8]{inputenc}
\usepackage[english,russian]{babel}

\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small#2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}
"""

    # Heading
    if contact_name or contact_phone or contact_email or contact_github:
        latex_content += r"""
%----------HEADING----------
\begin{center}
"""
        if contact_name:
            latex_content += r"\textbf{\Huge \scshape " + contact_name + r"} \\ \vspace{1pt}"
        if contact_phone:
            latex_content += r"\small " + contact_phone
        if contact_email or contact_github:
            latex_content += r" $|$ "
        if contact_email:
            latex_content += r"\href{mailto:" + contact_email + r"}{\underline{" + contact_email + r"}}"
        if contact_github:
            if contact_email:
                latex_content += r" $|$ "
            latex_content += r"\href{" + contact_github + r"}{\underline{" + contact_github + r"}}"
        latex_content += r"""
\end{center}
"""

    # Education Section
    if education_list:
        latex_content += r"""
%-----------EDUCATION-----------
\section{""" + section_titles['education'] + r"""}
\resumeSubHeadingListStart
"""
        for education in education_list:
            title = education.get('title', '')
            subtitle = education.get('subtitle', '')
            degree = education.get('degree', '')
            date_range = education.get('dateRange', '')
            if title or subtitle or degree or date_range:
                latex_content += r"""
\resumeSubheading
  {""" + (title or '') + r"""}{""" + (date_range or '') + r"""}
  {""" + (subtitle or '') + r"""}{""" + (degree or '') + r"""}
"""
        latex_content += r"\resumeSubHeadingListEnd"

    # Experience Section
    if experience_list:
        latex_content += r"""
%-----------EXPERIENCE-----------
\section{""" + section_titles['experience'] + r"""}
\resumeSubHeadingListStart
"""
        for experience in experience_list:
            position = experience.get('position', '')
            date_range = experience.get('dateRange', '')
            company = experience.get('company', '')
            location = experience.get('location', '')
            responsibilities = experience.get('responsibilities', [])
            if position or date_range or company or location:
                latex_content += r"""
\resumeSubheading
  {""" + (position or '') + r"""}{""" + (date_range or '') + r"""}
  {""" + (company or '') + r"""}{""" + (location or '') + r"""}
\resumeItemListStart
"""
                for responsibility in responsibilities:
                    latex_content += r"""
\resumeItem{""" + responsibility + r"""}
"""
                latex_content += r"\resumeItemListEnd"
        latex_content += r"\resumeSubHeadingListEnd"

    # Projects Section
    if projects_list:
        latex_content += r"""
%----------PROJECTS----------
\section{""" + section_titles['projects'] + r"""}
\resumeSubHeadingListStart
"""
        for project in projects_list:
            title = project.get('title', '')
            description = project.get('description', '')
            date_range = project.get('dateRange', '')
            descriptions = project.get('descriptions', [])
            if title or description or date_range:
                latex_content += r"""
\resumeProjectHeading
    {\textbf{""" + (title or '') + r"""} $|$ \emph{""" + (description or '') + r"""} }{""" + (date_range or '') + r"""}
\resumeItemListStart
"""
                for description in descriptions:
                    latex_content += r"""
\resumeItem{""" + description + r"""}
"""
                latex_content += r"\resumeItemListEnd"
        latex_content += r"\resumeSubHeadingListEnd"

    # Skills Section
    if skills_list:
        latex_content += r"""
%-----------TECHNICAL SKILLS-----------
\section{""" + section_titles['technical_skills'] + r"""}
\begin{itemize}[leftmargin=0.15in, label={}]
"""
        for skill in skills_list:
            title = skill.get('title', '')
            description = skill.get('description', '')
            if title or description:
                latex_content += r"""
\item \small{
\textbf{""" + (title or '') + r"""}{: """ + (description or '') + r"""}
}
"""
        latex_content += r"""
\end{itemize}
"""

    latex_content += r"""
\end{document}
"""

    return latex_content
