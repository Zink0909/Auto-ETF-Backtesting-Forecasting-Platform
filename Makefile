RUN ?= micromamba run -n etf-dca

.PHONY: run app test demo clean

run:           ## download prices + run the DCA analysis (uses configs/default.yaml)
	$(RUN) python -m etf_dca.run

demo:          ## same, but with the offline synthetic data source (no network)
	$(RUN) python -c "from etf_dca.config import Config; from etf_dca import run; \
c=Config.load(); c.raw['data']['source']='synthetic'; run.main(c)"

app:           ## launch the Streamlit app
	$(RUN) streamlit run app.py

test:
	$(RUN) python -m pytest -q

clean:
	rm -f reports/*.xlsx; rm -rf reports/figures data/cache
