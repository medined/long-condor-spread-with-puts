# Python

## Environment

### Creation

```
conda activate base
mamba env create --file=environment.yml
```

### Activate

```
conda activate long-condor-spread
```

### Update

```
conda activate base
mamba env update --file=environment.yml
conda activate long-condor-spread
```

### Deactivate

```
conda deactivate
```

### Delete

```
conda deactivate
conda remove --yes --name=long-condor-spread --all
```
