
import pandas as pd

def get_referenced_with_pages(key_list,big_docs_list,column_name='tool'):
    ref_dict={city:[] for city in list(set([i.metadata['source'].split('/')[-1] for i in big_docs_list])) }
    #page_dict={city:[] for city in list(set([i.metadata['source'].split('/')[-1] for i in big_docs_list])) }
    for mdoc in big_docs_list:
        for p in key_list:
            idx=mdoc.page_content.lower().find(p)
            if idx!=-1:
                #print(mdoc.metadata,p)
                source=mdoc.metadata['source'].split('/')[-1]
                page=mdoc.metadata['page']
                #print(source)
                #ref_dict[source].append(f'({p},{page+1})')
                ref_dict[source].append((p,page+1))
                #page_dict[source].append(str(page+1))
    ref_dict={i:list(set(ref_dict[i])) for i in ref_dict}
    df=pd.DataFrame({'pdf':[],column_name:[]})
    df[column_name]=df[column_name].astype('object')
    for i,c in enumerate(ref_dict):
        df.loc[i,'pdf']=c
        #df.loc[i,column_name]=';'.join(ref_dict[c])
        df.at[i,column_name]=ref_dict[c]
        #df.loc[i,f'{column_name}_pages']=','.join(page_dict[c])
        
    return df